from hydroserverpy.core.service import HydroServer
from pandas import DataFrame
from typing import Dict
import pandas as pd
from .base import Loader
import logging


class HydroServerLoader(HydroServer, Loader):
    """
    A class that extends the HydroServer client with ETL-specific functionalities.
    """

    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        apikey: str | None = None,
        api_route: str = "api",
    ):
        super().__init__(host, username, password, apikey, api_route)

    def load(self, data: DataFrame, source_target_map) -> None:
        """
        Load observations from a DataFrame to the HydroServer.

        :param data: A Pandas DataFrame where each column corresponds to a datastream.
        """
        data_requirements = self.get_data_requirements(source_target_map)
        for ds_id in data.columns:
            if ds_id == "timestamp":
                continue

            df = data[["timestamp", ds_id]].copy()
            df.rename(columns={ds_id: "value"}, inplace=True)
            df.dropna(subset=["value"], inplace=True)

            phenomenon_end_time = data_requirements[ds_id]["start_time"]
            if phenomenon_end_time:
                df = df[df["timestamp"] > phenomenon_end_time]
            if df.empty:
                logging.warning(
                    f"No new data to upload for datastream {ds_id}. Skipping."
                )
                continue
            self.datastreams.load_observations(uid=ds_id, observations=df)

    def get_data_requirements(self, source_target_map) -> Dict[str, pd.Timestamp]:
        """
        Each target system needs to be able to answer the question: 'What data do you need?'
        and return a time range for each target time series. Usually the answer will be
        'anything newer than my most recent observation'.
        """
        data_requirements = {}
        for ds_id in source_target_map.values():
            datastream = self.datastreams.get(uid=ds_id)
            if not datastream:
                message = "Couldn't fetch target datastream. ETL process aborted."
                logging.error(message)
                raise message
            start_time = pd.Timestamp(
                datastream.phenomenon_end_time or "1970-01-01T00:00:00Z"
            )
            end_time = pd.Timestamp.now()
            data_requirements[ds_id] = {"start_time": start_time, "end_time": end_time}
        return data_requirements
