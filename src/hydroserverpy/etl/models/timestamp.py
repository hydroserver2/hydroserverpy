import re
import pandas as pd
from datetime import datetime, timezone, timedelta, tzinfo
from zoneinfo import ZoneInfo
from typing import Literal, Optional
from pydantic import BaseModel, model_validator
from functools import cached_property


TimestampType = Literal["iso", "custom"]
TimezoneType = Literal["utc", "offset", "iana", "embedded"]

_OFFSET_RE = re.compile(r"^[+-](\d{4}|\d{2}:\d{2})$")


class Timestamp(BaseModel):
    timestamp_type: TimestampType = "iso"
    timestamp_format: Optional[str] = None
    timezone_type: TimezoneType = "utc"
    timezone: Optional[str] = None

    @model_validator(mode="after")
    def validate_timestamp_format(self) -> "Timestamp":
        if self.timestamp_type == "custom" and not self.timestamp_format:
            raise ValueError(
                "Invalid timestamp configuration. "
                "Timestamp format is required when the timestamp type is 'custom'."
            )
        elif self.timestamp_type != "custom" and self.timestamp_format:
            raise ValueError(
                "Invalid timestamp configuration. "
                "Timestamp formats may only be used when the timestamp type is 'custom'"
            )
        elif self.timestamp_type == "custom" and self.timestamp_format:
            self._validate_strftime_format(self.timestamp_format)

        return self

    @model_validator(mode="after")
    def validate_timezone(self) -> "Timestamp":
        if self.timezone_type in {"offset", "iana"} and not self.timezone:
            raise ValueError(
                "Invalid timezone configuration. "
                "Timezone offset must be provided when using IANA or UTC offsets"
            )
        elif self.timezone_type == "offset":
            self._validate_utc_offset(self.timezone)
        elif self.timezone_type == "iana":
            try:
                ZoneInfo(self.timezone)
            except Exception:
                raise ValueError(
                    f"Invalid IANA timezone '{self.timezone}' "
                    "(example: 'America/Denver')."
                )
        elif self.timezone_type == "embedded" and self.timezone is not None:
            raise ValueError(
                "Invalid timezone configuration. "
                "Default timezone value must not be provided when the "
                "timezone is expected to be embedded in the timestamp values."
            )

        return self

    @classmethod
    def _validate_utc_offset(cls, value: str) -> None:
        if not _OFFSET_RE.match(value):
            raise ValueError(
                f"Invalid timestamp UTC offset '{value}'. "
                "UTC offsets must be specified in ±HHMM or ±HH:MM format (e.g: '-0700' or '-07:00') "
                "with hours between 00 and 14 and minutes between 00 and 59."
            )

        clean = value.replace(":", "")
        hours = int(clean[1:3])
        minutes = int(clean[3:5])

        if hours > 14 or minutes >= 60 or (hours == 14 and minutes != 0):
            raise ValueError(
                f"Invalid timestamp UTC offset '{value}'. "
                "UTC offsets must be specified in ±HHMM or ±HH:MM format (e.g: '-0700' or '-07:00') "
                "with hours between 00 and 14 and minutes between 00 and 59."
            )

    @classmethod
    def _validate_strftime_format(cls, value: str) -> None:
        try:
            datetime(2000, 1, 1, 0, 0, 0).strftime(value)
        except Exception as e:
            raise ValueError(
                f"Invalid timestamp format string {value!r}. "
                "Ensure the string uses valid strftime directives "
                "(e.g., '%Y-%m-%d %H:%M:%S')."
            ) from e

    @staticmethod
    def _to_pandas_offset(value: str) -> str:
        """
        Normalise a UTC offset string to the ±HH:MM format required by pandas tz_localize.
        Accepts both ±HHMM and ±HH:MM as input.
        """

        if ":" in value:
            return value
        return f"{value[0]}{value[1:3]}:{value[3:5]}"

    @cached_property
    def tz(self) -> Optional[tzinfo]:
        """
        Return the configured timezone as a datetime.tzinfo instance.
        """

        if self.timezone_type == "offset":
            sign = 1 if self.timezone[0] == "+" else -1
            clean = self.timezone.replace(":", "")
            minutes = int(clean[1:3]) * 60 + int(clean[3:5])
            return timezone(timedelta(minutes=sign * minutes))
        elif self.timezone_type == "iana":
            return ZoneInfo(self.timezone)
        elif self.timezone_type == "utc":
            return timezone.utc
        else:
            return None

    def parse_series_to_utc(
        self,
        series: pd.Series
    ) -> pd.Series:
        """
        Parse a pandas Series of timestamps and normalize them to a UTC baseline.

        Parsing Logic:
        1. If timezone_type is 'embedded' or 'utc', strings are parsed as UTC-aware.
        2. If timezone_type is 'iana' or 'offset', strings are parsed as naive.

        Conflict Resolution:
        - Overwrite: If 'iana'/'offset' is configured but the data contains embedded
          timezones, the embedded offsets are stripped and replaced by the config.
        - Fallback: If 'embedded' is configured but the data is naive, UTC is assumed.
        - Type Safety: Mixed offsets are flattened into a consistent datetime64[ns, UTC]
          dtype to ensure the pandas .dt accessor remains available downstream.
        """

        # Ensure input is string-based for pandas parsing if not already datetime objects
        if not pd.api.types.is_datetime64_any_dtype(series):
            series: pd.Series = series.astype("string", copy=False).str.strip()

        # Determine if UTC parsing should be used directly
        parse_as_utc = self.timezone_type in ["embedded", "utc"]

        # Perform initial parsing of the values
        if self.timestamp_type == "iso":
            parsed_series = pd.to_datetime(series, utc=parse_as_utc, errors="coerce")
        else:
            parsed_series = pd.to_datetime(series, utc=parse_as_utc, format=self.timestamp_format, errors="coerce")

        # Apply fixed IANA or UTC offsets to the series if provided
        if self.timezone_type in ["offset", "iana"]:
            if parsed_series.dt.tz is not None or parsed_series.dtype == "object":
                parsed_series = parsed_series.dt.tz_localize(None)
            tz_label = self._to_pandas_offset(self.timezone) if self.timezone_type == "offset" else self.timezone
            utc_series = parsed_series.dt.tz_localize(tz_label, ambiguous="infer").dt.tz_convert(timezone.utc)

        # Normalize to UTC if the series timezones are embedded or naive and configured as UTC
        else:
            utc_series = pd.to_datetime(parsed_series, utc=True)

        return utc_series

#     def utc_to_string(self, dt: Union[datetime, pd.Timestamp]) -> str:
#         """
#         Convert a UTC datetime or pd.Timestamp to a custom string format.
#
#         Some external APIs are picky about their timestamp formats, so we need the ability to pull a
#         UTC timestamp from HydroServer and format it into a custom string.
#         """
#         if isinstance(dt, pd.Timestamp):
#             dt = dt.to_pydatetime()
#
#         tz_format = self.timestamp.format.lower()
#         if tz_format == "iso8601":
#             return dt.astimezone(timezone.utc).isoformat()
#
#         if tz_format == "naive":
#             return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
#
#         if tz_format == "custom":
#             logger.debug(
#                 "Formatting runtime timestamp using custom format (customFormat=%r, timezoneMode=%r, timezone=%r).",
#                 self.timestamp.custom_format,
#                 self.timestamp.timezone_mode,
#                 self.timestamp.timezone,
#             )
#             return dt.astimezone(self.tz).strftime(self.timestamp.custom_format)
#
#         raise ValueError(f"Unknown timestamp.format: {self.timestamp.format!r}")
