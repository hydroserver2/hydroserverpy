from io import StringIO
import logging
import pandas as pd
from typing import Iterable, Union
from .base import Transformer


class CSVTransformer(Transformer):
    def __init__(self, settings: object):
        # Pandas is zero-based while CSV is one-based so convert
        self.delimiter = settings.get("delimiter", ",")
        self.header_row = (
            None if settings.get("headerRow") is None else settings["headerRow"] - 1
        )
        self.data_start_row = (
            settings["dataStartRow"] - 1 if "dataStartRow" in settings else 0
        )
        self.timestamp_column = self.convert_to_zero_based(settings["timestampKey"])
        # TODO: Add a timestamp formatter that will convert the timestamp based on the format
        format_map = {
            "utc": "ISO8601",
            "constant": None,
            "ISO8601": "ISO8601",
            "custom": settings.get("customFormatString"),
        }
        self.timestamp_format = format_map.get(settings.get("timestampFormat"))
        self.timestamp_offset = settings.get("timestampOffset", "+0000")
        self.identifier_type = settings.get("identifierType", "name")

    def transform(self, data_file, mappings) -> Union[pd.DataFrame, None]:
        """
        Transforms a CSV file-like object into a Pandas DataFrame where the column
        names are replaced with their target datastream ids.

        Parameters:
            data_file: File-like object containing CSV data.
        Returns:
            observations_map (dict): Dict mapping datastream IDs to pandas DataFrames.
        """

        clean_file = self._strip_comments(data_file)
        source_identifiers = [mapping["sourceIdentifier"] for mapping in mappings]

        try:
            df = pd.read_csv(
                clean_file,
                sep=self.delimiter,
                header=self.header_row,
                parse_dates=[self.timestamp_column],
                skiprows=self._build_skiprows(),
                usecols=[self.timestamp_column] + source_identifiers,
            )
            logging.info(f"extracted CSV file: {df.shape}")
        except Exception as e:
            logging.error(f"Error reading CSV data: {e}")
            return None

        if self.header_row is None:
            df.columns = list(range(1, len(df.columns) + 1))

        # TODO: for constant formats, append the timestamp_offset to each timestamp
        return self.standardize_dataframe(
            df, mappings, self.timestamp_column, self.timestamp_format
        )

    def _strip_comments(self, stream: Iterable[Union[str, bytes]]) -> StringIO:
        """
        Remove lines whose first non-blank char is '#'.
        Works for both text and binary iterables.
        """
        clean: list[str] = []

        for raw in stream:
            # normalize to bytes
            b = raw if isinstance(raw, bytes) else raw.encode("utf-8", "ignore")
            if b.lstrip().startswith(b"#"):
                continue
            clean.append(
                raw.decode("utf-8", "ignore") if isinstance(raw, bytes) else raw
            )

        return StringIO("".join(clean))

    def _build_skiprows(self):
        return lambda idx: idx != self.header_row and idx < self.data_start_row

    @staticmethod
    def convert_to_zero_based(index: Union[str, int]) -> Union[str, int]:
        if isinstance(index, int):
            return index - 1
        return index
