import datetime
from hydroserverpy import HydroServer
from typing import Dict, Optional

from src.hydroserverpy.etl.types import TimeRange
from .base import Loader
import logging
import pandas as pd


class HydroServerLoader(HydroServer, Loader):
    """
    A class that extends the HydroServer client with ETL-specific functionalities.
    """

    def __init__(
        self,
        host: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        apikey: Optional[str] = None,
    ):
        super().__init__(
            host=host,
            email=email,
            password=password,
            apikey=apikey,
        )

    def load(self, data: pd.DataFrame, payload_settings) -> None:
        """
        Load observations from a DataFrame to the HydroServer.

        :param data: A Pandas DataFrame where each column corresponds to a datastream.
        """
        mappings = payload_settings["mappings"]
        time_ranges = self.get_data_requirements(mappings)
        for ds_id in data.columns:
            if ds_id == "timestamp":
                continue

            df = data[["timestamp", ds_id]].copy()
            df.rename(columns={ds_id: "value"}, inplace=True)
            df.dropna(subset=["value"], inplace=True)

            # ensure the timestamp column is UTC‑aware
            timestamp_column = df["timestamp"]
            if timestamp_column.dt.tz is None:
                df["timestamp"] = timestamp_column.dt.tz_localize("UTC")

            tr = time_ranges[ds_id]
            start_ts = pd.to_datetime(tr["start_time"], utc=True)

            if start_ts:
                df = df[df["timestamp"] > start_ts]
            logging.info(f"start cutoff for data loading {start_ts}")
            if df.empty:
                logging.warning(
                    f"No new data to upload for datastream {ds_id}. Skipping."
                )
                continue
            self.datastreams.load_observations(uid=ds_id, observations=df)

    def get_data_requirements(self, source_target_map) -> Dict[str, TimeRange]:
        """
        Each target system needs to be able to answer the question: 'What data do you need?'
        and return a time range for each target time series. Usually the answer will be
        'anything newer than my most recent observation'.
        """
        data_requirements = {}
        target_ids = [mapping["targetIdentifier"] for mapping in source_target_map]
        for id in target_ids:
            datastream = self.datastreams.get(uid=id)
            if not datastream:
                message = "Couldn't fetch target datastream. ETL process aborted."
                logging.error(message)
                raise message

            start_ts = pd.Timestamp(
                datastream.phenomenon_end_time or "1970-01-01T00:00:00Z"
            )
            if start_ts.tzinfo is None:
                start_ts = start_ts.tz_localize("UTC")

            end_ts = pd.Timestamp.now(tz="UTC")

            data_requirements[id] = {
                "start_time": start_ts.isoformat(),
                "end_time": end_ts.isoformat(),
            }
        return data_requirements
