import logging

# import croniter
import pandas as pd
from typing import TYPE_CHECKING, Dict, Optional, TypedDict

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
ObservationsMap = Dict[str, Optional[pd.DataFrame]]
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
    """
    TODO: Validate input data_source file -
            Validate each datastream_id has a live datastream.
            Validate the number of datastream_ids match the number of measurement types.
    TODO: An admin may delete a datastream, but still have it listed in the orchestrator.
            This shouldn't bring down the entire system so we should skip ETL for missing
            datastreams & report an error.
    """

    def __init__(self, extractor, transformer, loader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    async def run(self):
        """
        Extracts and transforms data as defined by the class parameters and
        loads them into a HydroServer database instance.

        :param self
        :return: None
        """

        # Step 1: Establish a connection with the remote host if there is one
        # Step 2: Request data from host
        data = await self.extractor.extract()

        # Step 3: Transform response into native type
        if self.transformer:
            if self.transformer.needs_datastreams:
                datastreams = self.loader.datastreams.list(owned_only=True)
                if not datastreams:
                    logging.error("No datastreams fetched. ETL process aborted.")
                    return

                datastream_ids = set(self.transformer.datastream_ids.values())
                filtered_datastreams = [
                    ds for ds in datastreams if str(ds.uid) in datastream_ids
                ]

                datastreams = {str(ds.uid): ds for ds in filtered_datastreams}
                data: ObservationsMap = self.transformer.transform(data, datastreams)
            else:
                data: ObservationsMap = self.transformer.transform(data)

        # Step 4: Upload to HydroServer API
        for id, observations in data.items():
            self.loader.datastreams.load_observations(uid=id, observations=observations)
