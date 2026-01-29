from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Loader
import logging
import pandas as pd
from ..etl_configuration import Task, SourceTargetMapping

if TYPE_CHECKING:
    from hydroserverpy.api.client import HydroServer


class HydroServerLoader(Loader):
    """
    A class that extends the HydroServer client with ETL-specific functionalities.
    """

    def __init__(self, client: HydroServer, task_id):
        self.client = client
        self._begin_cache: dict[str, pd.Timestamp] = {}
        self.task_id = task_id

    def load(self, data: pd.DataFrame, task: Task) -> None:
        """
        Load observations from a DataFrame to the HydroServer.
        :param data: A Pandas DataFrame where each column corresponds to a datastream.
        """
        begin_date = self.earliest_begin_date(task)
        new_data = data[data["timestamp"] > begin_date]
        for col in new_data.columns.difference(["timestamp"]):
            datastream = self.client.datastreams.get(
                uid=str(col)
            )
            ds_cutoff = datastream.phenomenon_end_time
            df = (
                new_data[["timestamp", col]]
                .loc[lambda d: d["timestamp"] > ds_cutoff if ds_cutoff else True]
                .rename(columns={col: "value"})
                .dropna(subset=["value"])
            )
            if df.empty:
                logging.warning(f"No new data for {col}, skipping.")
                continue

            df = df.rename(columns={"timestamp": "phenomenon_time", "value": "result"})

            # Chunked upload
            CHUNK_SIZE = 5000
            total = len(df)
            for start in range(0, total, CHUNK_SIZE):
                end = min(start + CHUNK_SIZE, total)
                chunk = df.iloc[start:end]
                logging.info(
                    "Uploading %s rows (%s-%s) to datastream %s",
                    len(chunk),
                    start,
                    end - 1,
                    col,
                )
                try:
                    self.client.datastreams.load_observations(
                        uid=str(col), observations=chunk
                    )
                except Exception as e:
                    status = getattr(e, "status_code", None) or getattr(
                        getattr(e, "response", None), "status_code", None
                    )
                    if status == 409 or "409" in str(e) or "Conflict" in str(e):
                        logging.info(
                            "409 Conflict for datastream %s on rows %s-%s; skipping remainder for this stream.",
                            col,
                            start,
                            end - 1,
                        )
                    raise

    def _fetch_earliest_begin(
        self, mappings: list[SourceTargetMapping]
    ) -> pd.Timestamp:
        logging.info("Querying HydroServer for earliest begin date for task...")
        timestamps = []
        for m in mappings:
            for p in m["paths"] if isinstance(m, dict) else m.paths:
                datastream_id = p["targetIdentifier"] if isinstance(p, dict) else p.target_identifier
                datastream = self.client.datastreams.get(datastream_id)
                raw = datastream.phenomenon_end_time or "1970-01-01"
                ts = pd.to_datetime(raw, utc=True)
                timestamps.append(ts)
        logging.info(f"Found earliest begin date: {min(timestamps)}")
        return min(timestamps)

    def earliest_begin_date(self, task: Task) -> pd.Timestamp:
        """
        Return earliest begin date for a task, or compute+cache it on first call.
        """
        key = task.name
        if key not in self._begin_cache:
            self._begin_cache[key] = self._fetch_earliest_begin(task.mappings)
        return self._begin_cache[key]
