from abc import ABC, abstractmethod
from datetime import timedelta, timezone
import logging
from typing import Union
import pandas as pd


class Transformer(ABC):
    def __init__(self, settings: object):
        # timestampFormat will be the strs: 'utc', 'ISO8601', 'constant', or some custom openStrftime.
        # If 'constant', then the system will append the timestamp_offset to the end of it.
        self.timestamp_format = settings.get("timestampFormat", "ISO8601")
        self.timestamp_offset: str = settings.get("timestampOffset", "+0000")
        self.timestamp_key: Union[str, int] = settings["timestampKey"]

        if isinstance(self.timestamp_key, int):
            # Users will always interact in 1-based, so if the key is a column index, convert to 0-based
            self.timestamp_key = self.timestamp_key - 1

    @abstractmethod
    def transform(self, *args, **kwargs) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        return False

    def standardize_dataframe(self, df, payload_mappings):
        rename_map = {
            mapping["sourceIdentifier"]: mapping["targetIdentifier"]
            for mapping in payload_mappings
        }

        df.rename(
            columns={self.timestamp_key: "timestamp", **rename_map},
            inplace=True,
        )

        # Verify timestamp column is present in the DataFrame
        if "timestamp" not in df.columns:
            message = f"Timestamp column '{self.timestamp_key}' not found in data."
            logging.error(message)
            raise ValueError(message)

        # verify datastream columns
        expected = set(rename_map.values())
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(
                "The following datastream IDs are specified in the config file but their related keys could not be "
                f"found in the source system's extracted data: {missing}"
            )

        # keep only timestamp + datastream columns; remove the rest inplace
        to_keep = ["timestamp", *expected]
        df.drop(columns=df.columns.difference(to_keep), inplace=True)

        df["timestamp"] = self._parse_timestamps(df["timestamp"])

        df.drop_duplicates(subset=["timestamp"], keep="last")
        logging.info(f"standardized dataframe created: {df.shape}")
        logging.info(f"{df.info()}")
        logging.info(f"{df.head()}")

        return df

    def _parse_timestamps(self, raw_series: pd.Series) -> pd.Series:
        """Return a Series of pandas UTC datetimes for the four supported modes."""
        logging.info(f"parsing timestamps. Format: {self.timestamp_format}")

        fmt = self.timestamp_format.lower()

        VALID_KEYS = {"utc", "iso8601", "constant"}
        if fmt not in VALID_KEYS and "%" not in self.timestamp_format:
            raise ValueError(
                f"timestamp_format must be one of {', '.join(VALID_KEYS)} "
                "or a valid strftime pattern."
            )

        series = raw_series.str.strip()

        if fmt == "utc":
            # Accept Z-suffix, no offset, fractional seconds, etc.
            parsed = pd.to_datetime(series, utc=True, errors="coerce")

        elif fmt == "iso8601":
            # pandas reads the embedded offset, then we shift to UTC
            parsed = pd.to_datetime(series, errors="coerce").dt.tz_convert("UTC")

        elif fmt == "constant":
            offset = str(self.timestamp_offset).strip()
            if not (len(offset) == 5 and offset[0] in "+-"):
                raise ValueError(f"Invalid timestampOffset: {self.timestamp_offset}")

            sign_multiplier = 1 if offset[0] == "+" else -1
            hours = int(offset[1:3])
            minutes = int(offset[3:5])
            total_minutes = sign_multiplier * (hours * 60 + minutes)
            local_timezone = timezone(timedelta(minutes=total_minutes))

            naive_times = pd.to_datetime(series, errors="coerce")
            localized_times = naive_times.dt.tz_localize(local_timezone)
            parsed = localized_times.dt.tz_convert("UTC")

        else:
            logging.info(f"timestamp format is custom {self.timestamp_format}")
            parsed = pd.to_datetime(
                series, format=self.timestamp_format, errors="coerce"
            ).dt.tz_localize("UTC")

        if parsed.isna().any():
            bad_rows = series[parsed.isna()].head(5).tolist()
            logging.warning(
                f"{parsed.isna().sum()} timestamps failed to parse. Sample bad values: {bad_rows}"
            )

        return parsed
