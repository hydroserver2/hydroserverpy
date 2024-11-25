import logging
import pandas as pd
from typing import Dict, Optional, TypedDict


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

"""
TODO: Validate input data_source file -
        Validate each datastream_id has a live datastream.
        Validate the number of datastream_ids match the number of measurement types.
TODO: An admin may delete a datastream, but still have it listed in the orchestrator.
        This shouldn't bring down the entire system so we should skip ETL for missing
        datastreams & report an error.
"""


class HydroServerETL:
    def __init__(self, extractor, transformer, loader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self):
        """
        Extracts and transforms data as defined by the class parameters and
        loads them into a HydroServer database instance.

        :param self
        :return: None
        """

        if self.extractor.needs_datastreams or self.transformer.needs_datastreams:
            # TODO: instead of fetching all the datastreams and filtering, just get the ones we need.
            datastreams = self.loader.datastreams.list(owned_only=True)
            if not datastreams:
                logging.error("No datastreams fetched. ETL process aborted.")
                raise "No datastreams fetched. ETL process aborted."

            datastream_ids = set(self.transformer.datastream_ids.values())
            filtered_datastreams = [
                ds for ds in datastreams if str(ds.uid) in datastream_ids
            ]

            datastreams = {str(ds.uid): ds for ds in filtered_datastreams}

        # Step 1: Establish a connection with the remote host if there is one
        # Step 2: Request data from host
        if self.extractor.needs_datastreams:
            data = self.extractor.extract(datastreams=datastreams)
        else:
            data = self.extractor.extract()

        if not data:
            logging.warning(f"No data was returned from the extractor.")
            return
        else:
            logging.info(f"Successfully extracted data.")

        # Step 3: Transform response into native type
        if self.transformer:
            if self.transformer.needs_datastreams:
                data: ObservationsMap = self.transformer.transform(data, datastreams)
            else:
                data: ObservationsMap = self.transformer.transform(data)

            if not data:
                logging.warning(f"No data was returned from the transformer.")
                return
            else:
                logging.info(f"Successfully transformed data.")

        # Step 4: Upload to HydroServer API
        for id, observations in data.items():
            self.loader.datastreams.load_observations(uid=id, observations=observations)
