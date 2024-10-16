import csv
import logging
from typing import List, Dict
from datetime import datetime, timezone
from .base import Transformer
from dateutil.parser import isoparse


class CSVTransformer(Transformer):
    def __init__(self):
        # TODO: We probably don't need these since Airflow can handle errors and logging
        self._message = None
        self._failed_datastreams = []
        self._file_header_error = False
        self._file_timestamp_error = False

        # TODO: get this working with the new setup
        self._chunk_size = 10000
        self._observations = {}

    def transform(self, data_file):
        data_reader = csv.reader(data_file, delimiter=self.delimiter)

        try:
            for i, row in enumerate(data_reader):

                # Parse through the data file to get header info and start reading observations.
                self._parse_data_file_row(i + 1, row)

                # Post chunked observations once chunk size has been reached.
                if i > 0 and i % self._chunk_size == 0:
                    self._failed_datastreams.extend(self._post_observations())

        except HeaderParsingError as e:
            self._message = f"Failed to parse header for {self._data_source.name} with error: {str(e)}"
            logging.error(self._message)
            self._file_header_error = True

        except TimestampParsingError as e:
            self._message = f"Failed to parse one or more timestamps for {self._data_source.name} with error: {str(e)}"
            logging.error(self._message)
            self._file_timestamp_error = True

        # Post final chunk of observations after file has been fully parsed.
        self._failed_datastreams.extend(self._post_observations())

        if not self._message and len(self._failed_datastreams) > 0:
            self._message = f"One or more datastreams failed to sync with HydroServer for {self._data_source.name}."

        self._update_data_source()

    def parse_header(self, header_row: List[str]) -> None:
        """Parse the CSV header row to find column indexes for timestamp and datastreams."""
        try:
            # Determine the index of the timestamp column
            if isinstance(self._data_source.timestamp_column, str):
                self._timestamp_column_index = header_row.index(
                    self._data_source.timestamp_column
                )
            else:
                self._timestamp_column_index = (
                    int(self._data_source.timestamp_column) - 1
                )
            if self._timestamp_column_index >= len(header_row):
                raise ValueError("Timestamp column index out of range.")

            # Determine the indexes of datastream columns
            for datastream in self._data_source.datastreams:
                if isinstance(datastream.data_source_column, str):
                    index = header_row.index(datastream.data_source_column)
                else:
                    index = int(datastream.data_source_column) - 1
                if index >= len(header_row):
                    raise ValueError(
                        f"Datastream column index out of range for {datastream.uid}."
                    )
                self._datastream_column_indexes[str(datastream.uid)] = index

        except ValueError as e:
            raise HeaderParsingError(f"Error parsing header: {e}") from e

    def parse_row(self, row: List[str]) -> Dict:
        """Parse a CSV data row into a standardized format."""
        try:
            # Parse the timestamp
            timestamp_str = row[self._timestamp_column_index]
            timestamp_format = (
                self._data_source.timestamp_format or "%Y-%m-%dT%H:%M:%S%z"
            )
            if timestamp_format.lower() == "iso":
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.strptime(timestamp_str, timestamp_format)
        except ValueError as e:
            raise TimestampParsingError(f"Error parsing timestamp: {e}") from e

        # Collect values for each datastream
        values = {}
        for datastream_id, index in self._datastream_column_indexes.items():
            try:
                values[datastream_id] = float(row[index])
            except (ValueError, IndexError) as e:
                values[datastream_id] = None  # Handle missing or invalid data

        return {"timestamp": timestamp, "values": values}

    def _parse_file_header(self, row: List[str]) -> None:
        """
        The _parse_file_header function is used to parse the header of a file.
        It takes in a row (a list of strings) and parses it for the timestamp column index,
        and datastream column indexes. It then sets these values as attributes on self._timestamp_column_index,
        and self._datastream_column_indexes respectively.

        :param self: Refer to the object itself
        :param row: List[str]: Parse the header of a csv file
        :return: A dictionary of the datastreams with their column index
        """

        try:
            self._timestamp_column_index = (
                row.index(self._data_source.timestamp_column)
                if isinstance(self._data_source.timestamp_column, str)
                else int(self._data_source.timestamp_column) - 1
            )
            if self._timestamp_column_index > len(row):
                raise ValueError
            self._datastream_column_indexes = {
                datastream.data_source_column: (
                    row.index(datastream.data_source_column)
                    if not datastream.data_source_column.isdigit()
                    else int(datastream.data_source_column) - 1
                )
                for datastream in self._datastreams.values()
            }
            if len(self._datastream_column_indexes.values()) > 0 and max(
                self._datastream_column_indexes.values()
            ) > len(row):
                raise ValueError
        except ValueError as e:
            logging.error(
                f'Failed to load data from data source: "{self._data_source.name}"'
            )
            raise HeaderParsingError(str(e)) from e

    def _parse_row_timestamp(self, row: List[str]) -> datetime:
        """
        The _parse_row_timestamp function takes a row of data from the CSV file and parses it into a datetime object.

        :param self
        :param row: List[str]: Parse the timestamp from a row of data
        :return: A datetime object, which is a python standard library class
        """

        try:
            if (
                self._data_source.timestamp_format == "iso"
                or self._data_source.timestamp_format is None
            ):
                timestamp = isoparse(row[self._timestamp_column_index])
            else:
                timestamp = datetime.strptime(
                    row[self._timestamp_column_index],
                    self._data_source.timestamp_format,
                )
        except ValueError as e:
            raise TimestampParsingError(str(e)) from e

        if timestamp.tzinfo is None:
            if not self._data_source.timestamp_offset:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                try:
                    timestamp = timestamp.replace(
                        tzinfo=datetime.strptime(
                            self._data_source.timestamp_offset[:-2]
                            + ":"
                            + self._data_source.timestamp_offset[3:],
                            "%z",
                        ).tzinfo
                    )
                except ValueError as e:
                    logging.error(
                        f'Failed to load data from data source: "{self._data_source.name}"'
                    )
                    raise TimestampParsingError(str(e)) from e

        return timestamp

    def _parse_data_file_row(self, index: int, row: List[str]) -> None:
        """
        The parse_data_file_row function is used to parse the data file row by row. The function takes in two
        arguments: index and row. The index argument is the current line number of the data file, and it's used to
        determine if we are at a header or not (if so, then we need to determine the column index for each named
        column). The second argument is a list containing all the values for each column on that particular line. If
        this isn't a header, then we check if there are any observations with timestamps later than the latest
        timestamp for the associated datastream; if so, then add them into our observation_bodies to be posted.

        :param self
        :param index: Keep track of the row number in the file
        :param row: Access the row of data in the csv file
        :return: A list of datetime and value pairs for each datastream
        """

        if index == self._data_source.header_row or (
            index == self._data_source.data_start_row
            and self._timestamp_column_index is None
        ):
            self._parse_file_header(row)

        if index < self._data_source.data_start_row:
            return

        timestamp = self._parse_row_timestamp(row)

        for datastream in self._datastreams.values():
            if str(datastream.uid) not in self._datastream_start_row_indexes.keys():
                if (
                    not datastream.phenomenon_end_time
                    or timestamp > datastream.phenomenon_end_time
                ):
                    self._datastream_start_row_indexes[str(datastream.uid)] = index

            if (
                str(datastream.uid) in self._datastream_start_row_indexes.keys()
                and self._datastream_start_row_indexes[str(datastream.uid)] <= index
            ):
                if str(datastream.uid) not in self._observations.keys():
                    self._observations[str(datastream.uid)] = []

                self._observations[str(datastream.uid)].append(
                    {
                        "phenomenon_time": timestamp,
                        "result": row[
                            self._datastream_column_indexes[
                                datastream.data_source_column
                            ]
                        ],
                    }
                )


class HeaderParsingError(Exception):
    """
    Raised when the header of a CSV file cannot be parsed due to incorrect field names or out of range index values.
    """

    pass


class TimestampParsingError(Exception):
    """
    Raised when the timestamp of a CSV file row cannot be parsed.
    """

    pass
