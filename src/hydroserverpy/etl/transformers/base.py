from abc import ABC, abstractmethod
import logging
import pandas as pd


class Transformer(ABC):
    @abstractmethod
    def transform(self, *args, **kwargs) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        return False

    @staticmethod
    def standardize_dataframe(
        df,
        payload_mappings,
        timestamp_column: str = "timestamp",
        timestamp_format: str = "ISO8601",
    ):
        rename_map = {
            mapping["sourceIdentifier"]: mapping["targetIdentifier"]
            for mapping in payload_mappings
        }

        df.rename(
            columns={timestamp_column: "timestamp", **rename_map},
            inplace=True,
        )

        # Verify timestamp column is present in the DataFrame
        if "timestamp" not in df.columns:
            message = f"Timestamp column '{timestamp_column}' not found in data."
            logging.error(message)
            raise ValueError(message)

        # verify datastream columns
        # TODO: Log some warnings when a specified source identifier can't be found in the file.
        expected = set(rename_map.values())
        missing = expected - set(df.columns)

        if missing:
            raise ValueError(
                "The following datastream IDs are specified in the config file but their related keys could not be "
                f"found in the source system's extracted data: {missing}"
            )

        # keep only timestamp + datastream columns
        df = df[["timestamp", *expected]]

        # Convert timestamp column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], format=timestamp_format)

        return df
