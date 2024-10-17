import logging

# import croniter
import pandas as pd
from typing import List, TYPE_CHECKING, Dict, TypedDict

# from requests import HTTPError
# from datetime import datetime, timezone, timedelta

# if TYPE_CHECKING:
# from .parsers.base import DataParser

# logger = logging.getLogger("hydroserver_etl")
# logger.addHandler(logging.NullHandler())


class Observation(TypedDict):
    timestamp: pd.Timestamp
    value: float


# Map a list of observations to the related datastream ID
ObservationsMap = Dict[str, List[Observation]]
# data = {
#     "datastream_1": [
#         {"timestamp": pd.Timestamp("2024-10-02 11:00:00+00:00"), "value": 41.0},
#         {"timestamp": pd.Timestamp("2024-10-02 12:00:00+00:00"), "value": 42.5},
#     ],
#     "datastream_2": [
#         {"timestamp": pd.Timestamp("2024-10-02 11:00:00+00:00"), "value": 35.0},
#         {"timestamp": pd.Timestamp("2024-10-02 12:00:00+00:00"), "value": 36.1},
#     ],
# }


class HydroServerETL:
    def __init__(self, service, data_source):
        self._service = service
        self.data_source = data_source

    async def run(self):
        """
        This extracts and transforms data as defined by the data source and
        loads them into a HydroServer database instance.

        :param self
        :return: None
        """
        # TODO: Verify the data_source is valid -
        #       TODO: Make sure each datastream related to datastream_id is available.
        #       An admin may delete a datastream, but still have it listed in the orchestrator.
        #       This shouldn't bring down the entire system so we should skip ETL for missing
        #       datastreams & report an error.

        # Step 1: Establish a connection with the remote host if there is one
        # Step 2: Request data from host
        # Step 3: Transform response into native type
        observations_map: ObservationsMap = await self.data_source.get_data()
        logging.info(f"observations_map: {observations_map}")

        # Step 4: Upload to HydroServer API
        # for datastream_id, observations in observations_map.items():
        #     self._service.datastreams.load_observations(
        #         uid=datastream_id, observations=observations
        #     )

    # def _post_observations(self) -> List[str]:
    #     """
    #     The _post_observations function is used to post observations to the SensorThings API.
    #     The function returns a list of datastreams that failed to be posted.
    #     The function iterates through all datastreams in self._observations, which is a dictionary with keys being
    #     datastream IDs and values being lists of observation dictionaries (see _load_observations for more details).
    #     For each datastream, if it has not previously failed posting observations or if there are any new observations
    #     to post, the function posts the new observations to HydroServer using the SensorThings API.

    #     :param self
    #     :return: A list of failed datastreams
    #     """

    #     failed_datastreams = []

    #     for datastream_id, observations in self._observations.items():
    #         if datastream_id not in self._failed_datastreams and len(observations) > 0:

    #             logger.info(
    #                 f"Loading observations from "
    #                 + f'{observations[0]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} to '
    #                 + f'{observations[-1]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} for datastream: '
    #                 + f'{str(datastream_id)} in data source "{self._data_source.name}".'
    #             )

    #             observations_df = pd.DataFrame(
    #                 [
    #                     [observation["phenomenon_time"], observation["result"]]
    #                     for observation in observations
    #                 ],
    #                 columns=["timestamp", "value"],
    #             )

    #             try:
    #                 self._service.datastreams.load_observations(
    #                     uid=datastream_id,
    #                     observations=observations_df,
    #                 )
    #             except HTTPError:
    #                 failed_datastreams.append(datastream_id)

    #             if not self._last_loaded_timestamp or (
    #                 observations[-1]["phenomenon_time"]
    #                 and observations[-1]["phenomenon_time"]
    #                 > self._last_loaded_timestamp
    #             ):
    #                 self._last_loaded_timestamp = observations[-1]["phenomenon_time"]
    #         elif datastream_id in self._failed_datastreams:
    #             logger.info(
    #                 f"Skipping observations POST request from "
    #                 + f'{observations[0]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} to '
    #                 + f'{observations[-1]["phenomenon_time"].strftime("%Y-%m-%dT%H:%M:%S%z")} for datastream: '
    #                 + f'{str(datastream_id)} in data source "{self._data_source.name}",'
    #                 + f"due to previous failed POST request."
    #             )
    #     self._observations = {}
    #     return failed_datastreams

    # def _update_data_source(self):
    #     """
    #     The _update_data_source function updates the data source with information about the last sync.

    #     :param self
    #     :return: None
    #     """

    #     if self._data_source.crontab is not None:
    #         next_sync = croniter.croniter(
    #             self._data_source.crontab, datetime.now()
    #         ).get_next(datetime)
    #     elif (
    #         self._data_source.interval is not None
    #         and self._data_source.interval_units is not None
    #     ):
    #         next_sync = datetime.now() + timedelta(
    #             **{self._data_source.interval_units: self._data_source.interval}
    #         )
    #     else:
    #         next_sync = None

    #     self._data_source.data_source_thru = self._last_loaded_timestamp
    #     self._data_source.last_sync_successful = (
    #         True
    #         if not self._file_timestamp_error
    #         and not self._file_header_error
    #         and len(self._failed_datastreams) == 0
    #         else False
    #     )
    #     self._data_source.last_sync_message = self._message
    #     self._data_source.last_synced = datetime.now(timezone.utc)
    #     self._data_source.next_sync = next_sync

    #     self._data_source.save()
