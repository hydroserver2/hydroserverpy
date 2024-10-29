from datetime import datetime
import pandas as pd
import logging
from typing import Dict, Optional, Union
from .base import Transformer


class CSVTransformer(Transformer):
    def __init__(
        self,
        header_row: Optional[int],
        data_start_row: int,
        timestamp_column: Union[str, int],
        datastream_ids: Dict[Union[str, int], str],
        delimiter: Optional[str] = ",",
        timestamp_format: Optional[str] = "ISO8601",
    ):
        # Pandas is zero-based while CSV is one-based so convert
        self.header_row = None if header_row is None else header_row - 1
        self.data_start_row = data_start_row - 1
        self.timestamp_column = self.convert_to_zero_based(timestamp_column)
        self.datastream_ids = datastream_ids
        self.timestamp_format = timestamp_format
        self.delimiter = delimiter

    @property
    def needs_datastreams(self) -> bool:
        return True

    def transform(self, data_file, datastreams) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Transforms a CSV file-like object into the observations_map format.

        Parameters:
            data_file: File-like object containing CSV data.
        Returns:
            observations_map (dict): Dict mapping datastream IDs to pandas DataFrames.
        """

        try:
            df = pd.read_csv(
                data_file,
                delimiter=self.delimiter,
                header=self.header_row,
                parse_dates=[self.timestamp_column],
                date_format=self.timestamp_format,
                skiprows=self.calculate_skiprows(),
                usecols=[self.timestamp_column] + list(self.datastream_ids.keys()),
            )
        except Exception as e:
            logging.error(f"Error reading CSV data: {e}")
            return None

        df = self.rename_column_headers(df)

        self.datastreams = datastreams
        return self.build_observations_map(df)

    def rename_column_headers(self, df):
        # Assign default column names if there's no header row
        if self.header_row is None:
            df.columns = list(range(1, len(df.columns) + 1))

        if self.timestamp_column not in df.columns:
            logging.error(
                f"Timestamp column '{self.timestamp_column}' not found in data."
            )
            return None

        if self.timestamp_column != "timestamp":
            df.rename(columns={self.timestamp_column: "timestamp"}, inplace=True)
        return df

    def calculate_skiprows(self):
        """
        Calculates the skiprows parameter for pd.read_csv.

        Returns:
            skiprows (list or None): List of row indices to skip, or None if no rows need to be skipped.
        Raises:
            ValueError: If header_row is not compatible with data_start_row.
        """
        if self.data_start_row == 0:
            if self.header_row is not None:
                # Cannot have a header row if data starts at the first row
                raise ValueError(
                    "header_row must be None when data_start_row is 1 (first row)"
                )
            return None  # No rows to skip

        skiprows = list(range(self.data_start_row))

        if self.header_row is not None:
            if self.header_row >= self.data_start_row:
                raise ValueError("header_row must be less than data_start_row")
            if self.header_row in skiprows:
                # Do not skip the header row
                skiprows.remove(self.header_row)
        return skiprows

    def build_observations_map(self, df):
        observations_map = {}
        for column_name, datastream_id in self.datastream_ids.items():
            if column_name not in df.columns:
                logging.error(f"Datastream column '{column_name}' not found in file.")
                continue

            observations = df[["timestamp", column_name]].dropna()
            if observations.empty:
                logging.warning(f"No data found for input column {column_name}")
                continue

            observations = observations.rename(columns={column_name: "value"})
            observations = self.filter_out_old_data(datastream_id, observations)
            if observations is None or observations.empty:
                logging.info(f"No new observations to add for '{datastream_id}'.")
                continue
            observations_map[datastream_id] = observations
        return observations_map

    def filter_out_old_data(self, datastream_id, observations):
        datastream = self.datastreams.get(datastream_id)
        phenomenon_end_time = datastream.phenomenon_end_time
        if not phenomenon_end_time:
            return observations

        if not isinstance(phenomenon_end_time, pd.Timestamp):
            try:
                phenomenon_end_time = pd.to_datetime(phenomenon_end_time)
            except Exception as e:
                logging.error(
                    f"Invalid 'phenomenon_end_time' for datastream '{datastream_id}': {e}"
                )
                return None
        return observations[observations["timestamp"] > phenomenon_end_time]

    def convert_to_zero_based(self, index: Union[str, int]) -> Union[str, int]:
        if isinstance(index, int):
            return index - 1
        return index
