import logging
from datetime import datetime, timedelta, timezone
from typing import Union
import pandas as pd


class TimestampParser:
    def __init__(
        self, timestamp_format: str = "ISO8601", timestamp_offset: str = "+0000"
    ):
        VALID_KEYS = {"utc", "iso8601", "constant"}
        self.timestamp_offset = timestamp_offset
        self.timestamp_format = timestamp_format

        if (
            self.timestamp_format.lower() not in VALID_KEYS
            and "%" not in self.timestamp_format
        ):
            raise ValueError(
                f"timestamp_format must be one of {', '.join(VALID_KEYS)} "
                "or a valid strftime pattern."
            )

    def parse_series(self, raw_series: pd.Series) -> pd.Series:
        s = raw_series.str.strip()
        if self.timestamp_format.lower() == "utc":
            parsed = pd.to_datetime(s, utc=True, errors="coerce")

        elif self.timestamp_format.lower() == "iso8601":
            parsed = pd.to_datetime(s, errors="coerce").dt.tz_convert("UTC")

        elif self.timestamp_format.lower() == "constant":
            off = self.timestamp_offset.strip()
            if not (len(off) == 5 and off[0] in "+-"):
                raise ValueError(f"Invalid timestamp_offset: {off}")
            sign = 1 if off[0] == "+" else -1
            hrs, mins = int(off[1:3]), int(off[3:5])
            tz = timezone(timedelta(minutes=sign * (hrs * 60 + mins)))
            naive = pd.to_datetime(s, errors="coerce")
            parsed = naive.dt.tz_localize(tz).dt.tz_convert("UTC")

        else:
            parsed = pd.to_datetime(
                s, format=self.timestamp_format, errors="coerce"
            ).dt.tz_localize("UTC")

        if parsed.isna().any():
            bad_rows = s[parsed.isna()].head(5).tolist()
            logging.warning(
                f"{parsed.isna().sum()} timestamps failed to parse. "
                f"Sample bad values: {bad_rows}"
            )

        return parsed

    def format(self, dt: Union[datetime, pd.Timestamp]) -> str:
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()

        fmt = self.timestamp_format.lower()
        if fmt == "utc":
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

        if fmt == "iso8601":
            return dt.astimezone(timezone.utc).isoformat()

        if fmt == "constant":
            off = self.timestamp_offset.strip()
            sign = 1 if off[0] == "+" else -1
            hrs, mins = int(off[1:3]), int(off[3:5])
            tz = timezone(timedelta(minutes=sign * (hrs * 60 + mins)))
            return dt.astimezone(tz).strftime("%Y-%m-%dT%H:%M:%S")

        # custom strftime
        return dt.strftime(self.timestamp_format)
