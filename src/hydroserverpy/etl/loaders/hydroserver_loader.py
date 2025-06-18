from hydroserverpy import HydroServer
from typing import Optional

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
        self._begin_cache: dict[str, str] = {}

    def load(self, data: pd.DataFrame, payload) -> None:
        """
        Load observations from a DataFrame to the HydroServer.
        :param data: A Pandas DataFrame where each column corresponds to a datastream.
        """
        begin_date = self.earliest_begin_date(payload)
        new_data = data[data["timestamp"] > begin_date]
        for col in new_data.columns.difference(["timestamp"]):
            df = (
                new_data[["timestamp", col]]
                .rename(columns={col: "value"})
                .dropna(subset=["value"])
            )
            if df.empty:
                logging.warning(f"No new data for {col}, skipping.")
                continue
            logging.info(f"loading dataframe {df}")
            logging.info(f"dtypes: {df.dtypes}")

            df["value"] = pd.to_numeric(df["value"], errors="raise")
            self.datastreams.load_observations(uid=col, observations=df)

    def _fetch_earliest_begin(self, mappings: list[dict]) -> pd.Timestamp:
        timestamps = []
        for m in mappings:
            ds = self.datastreams.get(uid=m["targetIdentifier"])
            if not ds:
                raise RuntimeError(f"Datastream {m['targetIdentifier']} not found.")
            raw = ds.phenomenon_end_time or "1970-01-01"
            ts = pd.to_datetime(raw, utc=True)
            logging.info(f"timestamp {ts}")
            timestamps.append(ts)
        return min(timestamps)

    def earliest_begin_date(self, payload: dict) -> pd.Timestamp:
        """
        Return earliest begin date for a payload, or compute+cache it on first call.
        """
        key = payload["name"]
        if key not in self._begin_cache:
            self._begin_cache[key] = self._fetch_earliest_begin(payload["mappings"])
        return self._begin_cache[key]
