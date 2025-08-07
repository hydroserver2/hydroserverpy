from io import StringIO
import logging
import pandas as pd
from typing import Iterable, List, Union
from .base import Transformer
from ..etl_configuration import TransformerConfig, SourceTargetMapping


class CSVTransformer(Transformer):
    def __init__(self, transformer_config: TransformerConfig):
        super().__init__(transformer_config)

        # Pandas is zero-based while CSV is one-based so convert
        self.header_row = (
            None if self.cfg.header_row is None else self.cfg.header_row - 1
        )
        self.data_start_row = (
            self.cfg.data_start_row - 1 if self.cfg.data_start_row else 0
        )
        self.delimiter = self.cfg.delimiter or ","
        self.identifier_type = self.cfg.identifier_type or "name"

    def transform(
        self, data_file, mappings: List[SourceTargetMapping]
    ) -> Union[pd.DataFrame, None]:
        """
        Transforms a CSV file-like object into a Pandas DataFrame where the column
        names are replaced with their target datastream ids.

        Parameters:
            data_file: File-like object containing CSV data.
        Returns:
            observations_map (dict): Dict mapping datastream IDs to pandas DataFrames.
        """

        clean_file = self._strip_comments(data_file)
        source_identifiers = [m.source_identifier for m in mappings]

        try:
            # Pandas’ heuristics strip offsets and silently coerce failures to strings.
            # Reading as pure text guarantees we always start with exactly what was in the file.
            # Timestamps will be parsed at df standardization time.
            df = pd.read_csv(
                clean_file,
                sep=self.delimiter,
                header=self.header_row,
                skiprows=self._build_skiprows(),
                usecols=[self.timestamp_key] + source_identifiers,
                dtype={self.timestamp_key: "string"},
            )
            logging.info(f"CSV file read into dataframe: {df.shape}")
        except Exception as e:
            logging.error(f"Error reading CSV data: {e}")
            return None

        if self.header_row is None:
            df.columns = list(range(1, len(df.columns) + 1))

        return self.standardize_dataframe(df, mappings)

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
