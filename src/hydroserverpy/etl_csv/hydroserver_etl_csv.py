import csv
import math
import logging
import croniter
import pandas as pd
from typing import IO, List, TYPE_CHECKING
from requests import HTTPError
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse
from .exceptions import HeaderParsingError, TimestampParsingError
import warnings

if TYPE_CHECKING:
    from hydroserverpy.api.models import DataSource

logger = logging.getLogger("hydroserver_etl")
logger.addHandler(logging.NullHandler())


class HydroServerETLCSV:

    def __init__(
        self,
        service,
        data_file: IO[str],
        data_source: "DataSource",
    ):
        warnings.warn(
            "HydroServerETLCSV is deprecated and will be removed in a future version. "
            "Please use the new HydroServerETL class.",
            DeprecationWarning,
        )
        self._service = service
        self._data_file = data_file
        self._data_source = data_source
        self._datastreams = {
            datastream.uid: datastream for datastream in data_source.datastreams
        }

        self._datastream_mapping = {
            mapping["targetIdentifier"]: mapping["sourceIdentifier"]
            for payload in self._data_source.settings["payloads"]
            for mapping in payload.get("mappings", [])
        }

        self._timestamp_column_index = None
        self._datastream_column_indexes = None
        self._datastream_start_row_indexes = {}

        self._message = None
        self._failed_datastreams = []
        self._file_header_error = False
        self._file_timestamp_error = False

        self._chunk_size = 1000
        self._observations = {}

    def run(self):
        """
        The run function is the main function of this class. It reads in a data file and parses it into observations,
        which are then posted to HydroServer. The run function also updates the DataSource object with information about
        the sync process.

        :param self
        :return: None
        """

        data_reader = csv.reader(
            self._data_file,
            delimiter=self._data_source.settings["transformer"]["delimiter"],
        )

        try:
            for i, row in enumerate(data_reader):

                # Parse through the data file to get header info and start reading observations.
                self._parse_data_file_row(i + 1, row)

                # Post chunked observations once chunk size has been reached.
                if i > 0 and i % self._chunk_size == 0:
                    self._failed_datastreams.extend(self._post_observations())

        except HeaderParsingError as e:
            self._message = f"Failed to parse header for {self._data_source.name} with error: {str(e)}"
            logger.error(self._message)
            self._file_header_error = True

        except TimestampParsingError as e:
            self._message = f"Failed to parse one or more timestamps for {self._data_source.name} with error: {str(e)}"
            logger.error(self._message)
            self._file_timestamp_error = True

        # Post final chunk of observations after file has been fully parsed.
        self._failed_datastreams.extend(self._post_observations())

        if not self._message and len(self._failed_datastreams) > 0:
            self._message = f"One or more datastreams failed to sync with HydroServer for {self._data_source.name}."

        self._update_data_source()

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

        if index == self._data_source.settings["transformer"]["headerRow"] or (
            index == self._data_source.settings["transformer"]["dataStartRow"]
            and self._timestamp_column_index is None
        ):
            self._parse_file_header(row)

        if index < self._data_source.settings["transformer"]["dataStartRow"]:
            return

        timestamp = self._parse_row_timestamp(row)

        for datastream in self._datastreams.values():
            if index == self._data_source.settings["transformer"]["dataStartRow"]:
                datastream.sync_phenomenon_end_time()

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

                raw_result = row[
                    self._datastream_column_indexes[
                        self._datastream_mapping[str(datastream.uid)]
                    ]
                ]

                if isinstance(raw_result, (int, float)):
                    result = raw_result
                else:
                    try:
                        result = float(raw_result)
                    except (TypeError, ValueError):
                        result = datastream.no_data_value

                if math.isnan(result):
                    result = datastream.no_data_value

                self._observations[str(datastream.uid)].append(
                    {
                        "phenomenon_time": timestamp,
                        "result": result,
                    }
                )

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
                row.index(self._data_source.settings["transformer"]["timestampKey"])
                if isinstance(
                    self._data_source.settings["transformer"]["timestampKey"], str
                )
                else int(self._data_source.settings["transformer"]["timestampKey"]) - 1
            )
            if self._timestamp_column_index > len(row):
                raise ValueError
            self._datastream_column_indexes = {
                self._datastream_mapping[str(datastream.uid)]: (
                    row.index(self._datastream_mapping[str(datastream.uid)])
                    if not self._datastream_mapping[str(datastream.uid)].isdigit()
                    else int(self._datastream_mapping[str(datastream.uid)]) - 1
                )
                for datastream in self._datastreams.values()
            }
            if len(self._datastream_column_indexes.values()) > 0 and max(
                self._datastream_column_indexes.values()
            ) > len(row):
                raise ValueError
        except ValueError as e:
            logger.error(
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
                self._data_source.settings["transformer"].get("timestampFormat") in ["utc", "constant", "ISO8601"]
                or self._data_source.settings["transformer"].get("timestampFormat")
                is None
            ):
                timestamp = isoparse(row[self._timestamp_column_index])
            else:
                timestamp = datetime.strptime(
                    row[self._timestamp_column_index],
                    self._data_source.settings["transformer"].get("timestampFormat"),
                )
        except ValueError as e:
            raise TimestampParsingError(str(e)) from e

        if timestamp.tzinfo is None:
            if not self._data_source.settings["transformer"].get(
                "timestampOffset"
            ) or self._data_source.settings["transformer"].get(
                "timestampOffset"
            ).endswith(
                "0000"
            ):
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                try:
                    timestamp = timestamp.replace(
                        tzinfo=datetime.strptime(
                            self._data_source.settings["transformer"].get(
                                "timestampOffset"
                            )[:-2]
                            + ":"
                            + self._data_source.settings["transformer"].get(
                                "timestampOffset"
                            )[3:],
                            "%z",
                        ).tzinfo
                    )
                except ValueError as e:
                    logger.error(
                        f'Failed to load data from data source: "{self._data_source.name}"'
                    )
                    raise TimestampParsingError(str(e)) from e

        return timestamp

    def _post_observations(self) -> List[str]:
        """
        The _post_observations function is used to post observations to the SensorThings API.
        The function returns a list of datastreams that failed to be posted.
        The function iterates through all datastreams in self._observations, which is a dictionary with keys being
        datastream IDs and values being lists of observation dictionaries (see _load_observations for more details).
        For each datastream, if it has not previously failed posting observations or if there are any new observations
        to post, the function posts the new observations to HydroServer using the SensorThings API.

        :param self
        :return: A list of failed datastreams
        """

        failed_datastreams = []

        for datastream_id, observations in self._observations.items():
            if datastream_id not in self._failed_datastreams and len(observations) > 0:

                logger.info(
                    f"Loading observations from "
                    + f'{observations[0]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} to '
                    + f'{observations[-1]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} for datastream: '
                    + f'{str(datastream_id)} in data source "{self._data_source.name}".'
                )

                observations_df = pd.DataFrame(
                    [
                        [observation["phenomenon_time"], observation["result"]]
                        for observation in observations
                    ],
                    columns=["timestamp", "value"],
                )

                try:
                    self._service.datastreams.load_observations(
                        uid=datastream_id,
                        observations=observations_df,
                    )
                except HTTPError as e:
                    failed_datastreams.append(datastream_id)
                    logger.error(f"Failed to POST observations to datastream: {str(datastream_id)} - {e}")

            elif datastream_id in self._failed_datastreams:
                logger.info(
                    f"Skipping observations POST request from "
                    + f'{observations[0]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} to '
                    + f'{observations[-1]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} for datastream: '
                    + f'{str(datastream_id)} in data source "{self._data_source.name}",'
                    + f"due to previous failed POST request."
                )

        self._observations = {}

        return failed_datastreams

    def _update_data_source(self):
        """
        The _update_data_source function updates the data source with information about the last sync.

        :param self
        :return: None
        """

        if self._data_source.crontab is not None:
            next_run = croniter.croniter(
                self._data_source.crontab, datetime.now(timezone.utc)
            ).get_next(datetime)
        elif (
            self._data_source.interval is not None
            and self._data_source.interval_units is not None
        ):
            next_run = datetime.now(timezone.utc) + timedelta(
                **{self._data_source.interval_units: self._data_source.interval}
            )
        else:
            next_run = None

        self._data_source.last_run_successful = (
            True
            if not self._file_timestamp_error
            and not self._file_header_error
            and len(self._failed_datastreams) == 0
            else False
        )
        self._data_source.last_run_message = self._message
        self._data_source.last_run = datetime.now(timezone.utc)
        self._data_source.next_run = next_run

        self._data_source.save()
