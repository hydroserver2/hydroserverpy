import logging
import pandas as pd
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union, TextIO, Optional
from pydantic import BaseModel, Field
from ..models.base import ETLComponent
from ..models.timestamp import Timestamp
from ..models.temporal_aggregation import TemporalAggregation
from ..utils import summarize_list
from ..operations import DataOperation
from ..exceptions import ETLError


logger = logging.getLogger(__name__)


class ETLTargetPath(BaseModel):
    target_identifier: Union[str, int]
    data_operations: list[DataOperation] = Field(default_factory=list)


class ETLDataMapping(BaseModel):
    source_identifier: Union[str, int]
    target_paths: list[ETLTargetPath]


class Transformer(ETLComponent, Timestamp, ABC):
    timestamp_key: str
    temporal_aggregation: Optional[TemporalAggregation] = None

    @abstractmethod
    def transform(
        self,
        payload: Union[str, TextIO, BytesIO],
        data_mappings: list[ETLDataMapping],
        **kwargs
    ) -> pd.DataFrame:
        ...

    def standardize_dataframe(
        self,
        df: pd.DataFrame,
        data_mappings: list[ETLDataMapping],
    ) -> pd.DataFrame:
        """
        Normalize and transform an extracted DataFrame into the standardized format
        expected by the ETL pipeline.

        The input DataFrame is not modified beyond column renaming and timestamp
        normalization. The returned DataFrame contains floating-point target values
        with NaN used where values cannot be coerced or transformed.
        """

        logger.debug(
            "Standardizing extracted dataframe (rows=%s, columns=%s).",
            len(df),
            len(df.columns),
        )
        logger.debug(
            "Extracted dataframe columns (sample): %s",
            summarize_list(list(df.columns), max_items=30),
        )

        if not df.empty:
            # Avoid dumping full rows; just log a compact preview.
            preview = df.iloc[0].to_dict()
            for k, v in list(preview.items()):
                if isinstance(v, str) and len(v) > 128:
                    preview[k] = v[:128] + "...(truncated)"
            logger.debug("Extracted dataframe first-row preview: %s", preview)

        # 1) Normalize timestamp column
        if self.timestamp_key not in df.columns:
            raise ETLError(
                f"Transformer received invalid payload. "
                f"Column with name '{self.timestamp_key}' not found in data. Provided columns: "
                f"{summarize_list(list(df.columns), max_items=30)}"
            )
        df.rename(columns={self.timestamp_key: "timestamp"}, inplace=True)

        logger.debug(
            "Normalized timestamp column '%s' -> 'timestamp' (timezoneType=%r, format=%r).",
            self.timestamp_key, self.timezone_type, self.timestamp_format
        )

        df["timestamp"] = self.parse_series_to_utc(df["timestamp"])
        df = df.drop_duplicates(subset=["timestamp"], keep="last")  # TODO: This behavior should be configurable

        # Source target mappings may be one to many. Create a new column for each target and apply transformations
        transformed_df = pd.DataFrame(index=df.index)
        logger.debug(
            "Applying %s source mapping(s): %s",
            len(data_mappings),
            summarize_list([data_mapping.source_identifier for data_mapping in data_mappings], max_items=30),
        )
        for data_mapping in data_mappings:
            source_column = self.resolve_source_column(df, data_mapping.source_identifier)
            base = df[source_column]
            for target_path in data_mapping.target_paths:
                target_column = str(target_path.target_identifier)
                transformed_df[target_column] = self.apply_data_transformations(base, target_path)

        # Keep only timestamp + target columns
        df = pd.concat([df[["timestamp"]], pd.DataFrame(transformed_df)], axis=1)

        if self.temporal_aggregation:
            df = self.temporal_aggregation.apply(df)

        logger.debug("Standardized dataframe created: %s", df.shape)

        return df

    @staticmethod
    def resolve_source_column(df: pd.DataFrame, source_id: Union[str, int]) -> str:
        """
        Resolve a column identifier to a valid column name in a DataFrame.

        This function accepts either an integer index or a column name,
        validates that it exists in the DataFrame, and returns the
        corresponding column name from the DataFrame.
        """

        # Integer source IDs are treated as positional column indices unless the integer
        # also exists as a column label, in which case the label takes precedence.
        if isinstance(source_id, int) and source_id not in df.columns:
            try:
                return df.columns[source_id]
            except IndexError as e:
                raise ETLError(
                    f"Source index '{source_id}' is out of range ({len(df.columns)}) for extracted data. "
                    f"Extracted columns: {summarize_list(list(df.columns), max_items=30)}"
                ) from e

        if source_id not in df.columns:
            raise ETLError(
                f"Source column '{source_id}' not found in extracted data. "
                f"Extracted columns: {summarize_list(list(df.columns), max_items=30)}"
            )

        return source_id

    @staticmethod
    def apply_data_transformations(
        series: pd.Series,
        path: ETLTargetPath
    ) -> pd.Series:
        """
        Apply the configured sequence of data transformations for a target path to a Pandas Series.

        The input series is coerced to numeric values when its dtype is ``object``, with non-numeric
        values converted to NaN. Each transformation defined in ``target_path.data_transformations``
        is then applied in order. Supported transformation types include:

        - ``expression``: Applies an arithmetic expression to the series.
        - ``rating_curve``: Applies a rating curve lookup and interpolation.

        The returned series preserves the input index and contains floating-point values, with
        NaN used for values that cannot be coerced or transformed.
        """

        transformed_series = series

        if pd.api.types.is_string_dtype(series):
            transformed_series = pd.to_numeric(transformed_series, errors="coerce")

        for transformation in path.data_operations:
            transformed_series = transformation.apply(transformed_series)

        return transformed_series
