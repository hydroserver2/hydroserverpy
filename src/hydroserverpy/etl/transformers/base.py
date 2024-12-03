from abc import ABC, abstractmethod
import logging
import pandas as pd


class Transformer(ABC):
    @abstractmethod
    def transform(self) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        False

    def standardize_dataframe(
        self,
        df,
        datastream_ids,
        timestamp_column: str = "timestamp",
        timestamp_format: str = "ISO8601",
    ):
        df.rename(
            columns={timestamp_column: "timestamp", **datastream_ids},
            inplace=True,
        )

        # Verify timestamp column is present in the DataFrame
        if "timestamp" not in df.columns:
            message = f"Timestamp column '{timestamp_column}' not found in data."
            logging.error(message)
            raise ValueError(message)

        # Verify that all datastream_ids are present in the DataFrame
        expected_columns = set(datastream_ids.values())
        actual_columns = set(df.columns)
        missing_datastream_ids = expected_columns - actual_columns

        if missing_datastream_ids:
            raise ValueError(
                f"The following datastream IDs are specified in the config file but their related keys could not be found in the source system's extracted data: {missing_datastream_ids}"
            )

        # Keep only 'timestamp' and datastream_id columns
        columns_to_keep = ["timestamp"] + list(expected_columns)
        df = df[columns_to_keep]

        # Convert timestamp column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], format=timestamp_format)

        return df
