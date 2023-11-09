import csv
import logging
import frost_sta_client as fsc
from typing import IO, List
from datetime import datetime, timezone
from dateutil.parser import isoparse
from hydroserver.schemas.data_sources import DataSourceGetResponse
from hydroserver.schemas.datastreams import DatastreamGetResponse
from hydroserver.exceptions import HeaderParsingError, TimestampParsingError
from hydroserver.schemas.data_sources import DataSourcePatchBody

logger = logging.getLogger('hydroserver_etl')
logger.addHandler(logging.NullHandler())


class HydroServerETL:

    def __init__(
            self,
            service,
            data_file: IO[str],
            data_source: DataSourceGetResponse,
            datastreams: List[DatastreamGetResponse]
    ):
        self._service = service
        self._data_file = data_file
        self._data_source = data_source
        self._datastreams = {
            datastream.id: datastream for datastream in datastreams
        }

        self._timestamp_column_index = None
        self._datastream_column_indexes = None
        self._datastream_start_row_indexes = {}
        self._last_loaded_timestamp = self._data_source.data_source_thru

        self._message = None
        self._failed_datastreams = []
        self._file_header_error = False
        self._file_timestamp_error = False

        self._chunk_size = 10000
        self._observations = {}

    def run(self):
        """"""

        data_reader = csv.reader(self._data_file, delimiter=self._data_source.delimiter)

        try:
            for i, row in enumerate(data_reader):

                # Parse through the data file to get header info and start reading observations.
                self._parse_data_file_row(i + 1, row)

                # Post chunked observations once chunk size has been reached.
                if i > 0 and i % self._chunk_size == 0:
                    self._failed_datastreams.extend(self._post_observations())

        except HeaderParsingError as e:
            self._message = f'Failed to parse header for {self._data_source.name} with error: {str(e)}'
            logger.error(self._message)
            self._file_header_error = True

        except TimestampParsingError as e:
            self._message = f'Failed to parse one or more timestamps for {self._data_source.name} with error: {str(e)}'
            logger.error(self._message)
            self._file_timestamp_error = True

        # Post final chunk of observations after file has been fully parsed.
        self._failed_datastreams.extend(self._post_observations())

        if not self._message and len(self._failed_datastreams) > 0:
            self._message = f'One or more datastreams failed to sync with HydroServer for {self._data_source.name}.'

        self._update_data_source()

    def _parse_data_file_row(self, index: int, row: List[str]) -> None:
        """
        The parse_data_file_row function is used to parse the data file row by row. The function takes in two
        arguments: index and row. The index argument is the current line number of the data file, and it's used to
        determine if we are at a header or not (if so, then we need to determine the column index for each named
        column). The second argument is a list containing all the values for each column on that particular line. If
        this isn't a header, then we check if there are any observations with timestamps later than the latest
        timestamp for the associated datastream; if so, then add them into our observation_bodies to be posted.

        :param self: Refer to the object itself
        :param index: Keep track of the row number in the file
        :param row: Access the row of data in the csv file
        :return: A list of datetime and value pairs for each datastream
        """

        if index == self._data_source.header_row or (
                index == self._data_source.data_start_row and self._timestamp_column_index is None
        ):
            self._parse_file_header(row)

        if index < self._data_source.data_start_row:
            return

        timestamp = self._parse_row_timestamp(row)

        for datastream in self._datastreams.values():
            if str(datastream.id) not in self._datastream_start_row_indexes.keys():
                if not datastream.phenomenon_end_time or timestamp > datastream.phenomenon_end_time:
                    self._datastream_start_row_indexes[str(datastream.id)] = index

            if str(datastream.id) in self._datastream_start_row_indexes.keys() \
                    and self._datastream_start_row_indexes[str(datastream.id)] <= index:
                if str(datastream.id) not in self._observations.keys():
                    self._observations[str(datastream.id)] = []

                self._observations[str(datastream.id)].append({
                    'phenomenon_time': timestamp,
                    'result': row[self._datastream_column_indexes[datastream.data_source_column]]
                })

    def _parse_file_header(self, row: List[str]) -> None:
        """"""

        try:
            self._timestamp_column_index = row.index(self._data_source.timestamp_column) \
                if not self._data_source.timestamp_column.isdigit() \
                else int(self._data_source.timestamp_column) - 1
            if self._timestamp_column_index > len(row):
                raise ValueError
            self._datastream_column_indexes = {
                datastream.data_source_column: row.index(datastream.data_source_column)
                if not datastream.data_source_column.isdigit()
                else int(datastream.data_source_column) - 1
                for datastream in self._datastreams.values()
            }
            if len(self._datastream_column_indexes.values()) > 0 and \
                    max(self._datastream_column_indexes.values()) > len(row):
                raise ValueError
        except ValueError as e:
            raise HeaderParsingError(str(e)) from e

    def _parse_row_timestamp(self, row: List[str]) -> datetime:
        """"""

        try:
            if self._data_source.timestamp_format == 'iso':
                timestamp = isoparse(
                    row[self._timestamp_column_index]
                )
            else:
                timestamp = datetime.strptime(
                    row[self._timestamp_column_index],
                    self._data_source.timestamp_format
                )
        except ValueError as e:
            raise TimestampParsingError(str(e)) from e

        if timestamp.tzinfo is None:
            if not self._data_source.timestamp_offset:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )
            else:
                try:
                    timestamp = timestamp.replace(
                        tzinfo=datetime.strptime(
                            self._data_source.timestamp_offset[:-2] + ':' + self._data_source.timestamp_offset[3:], '%z'
                        ).tzinfo
                    )
                except ValueError as e:
                    raise TimestampParsingError(str(e)) from e

        return timestamp

    def _post_observations(self) -> List[str]:
        """"""

        failed_datastreams = []

        for datastream_id, observations in self._observations.items():
            if datastream_id not in self._failed_datastreams and len(observations) > 0:
                data_array_value = getattr(fsc.model, 'ext').data_array_value.DataArrayValue()

                datastream = fsc.Datastream(id=datastream_id)
                components = {data_array_value.Property.PHENOMENON_TIME, data_array_value.Property.RESULT}

                data_array_value.datastream = datastream
                data_array_value.components = components

                for observation in observations:
                    data_array_value.add_observation(fsc.Observation(
                        phenomenon_time=observation['phenomenon_time'].strftime('%Y-%m-%dT%H:%M:%S%z'),
                        result=observation['result'],
                        datastream=datastream
                    ))

                data_array_document = getattr(fsc.model, 'ext').data_array_document.DataArrayDocument()
                data_array_document.add_data_array_value(data_array_value)

                try:
                    self._service.sensorthings.observations().create(data_array_document)
                except KeyError:
                    failed_datastreams.append(datastream_id)

                if observations[-1]['phenomenon_time'] > self._last_loaded_timestamp:
                    self._last_loaded_timestamp = observations[-1]['phenomenon_time']

        self._observations = {}

        return failed_datastreams

    def _update_data_source(self):
        """"""

        updated_data_source = DataSourcePatchBody(
            data_source_thru=self._last_loaded_timestamp,
            last_sync_successful=(
                True if not self._file_timestamp_error and not self._file_header_error
                and len(self._failed_datastreams) == 0 else False
            ),
            last_sync_message=self._message,
            last_synced=datetime.now(timezone.utc),
            next_sync=None
        )

        self._service.data_sources.update(
            data_source_id=str(self._data_source.id),
            data_source_body=updated_data_source
        )
