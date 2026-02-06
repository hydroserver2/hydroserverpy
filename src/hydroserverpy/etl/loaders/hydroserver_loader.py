from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

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

    def load(self, data: pd.DataFrame, task: Task) -> Dict[str, Any]:
        """
        Load observations from a DataFrame to the HydroServer.
        :param data: A Pandas DataFrame where each column corresponds to a datastream.
        """
        begin_date = self.earliest_begin_date(task)
        new_data = data[data["timestamp"] > begin_date]

        cutoff_value = (
            begin_date.isoformat()
            if hasattr(begin_date, "isoformat")
            else str(begin_date)
        )
        stats: Dict[str, Any] = {
            "cutoff": cutoff_value,
            "timestamps_total": len(data),
            "timestamps_after_cutoff": len(new_data),
            "timestamps_filtered_by_cutoff": max(len(data) - len(new_data), 0),
            "observations_available": 0,
            "observations_loaded": 0,
            "observations_skipped": 0,
            "observations_filtered_by_end_time": 0,
            "datastreams_total": 0,
            "datastreams_available": 0,
            "datastreams_loaded": 0,
            "per_datastream": {},
        }

        for col in new_data.columns.difference(["timestamp"]):
            stats["datastreams_total"] += 1
            datastream = self.client.datastreams.get(uid=str(col))
            ds_cutoff = datastream.phenomenon_end_time

            base_df = (
                new_data[["timestamp", col]]
                .rename(columns={col: "value"})
                .dropna(subset=["value"])
            )
            pre_count = len(base_df)
            if ds_cutoff:
                base_df = base_df.loc[base_df["timestamp"] > ds_cutoff]

            filtered_by_end = pre_count - len(base_df)
            if filtered_by_end:
                stats["observations_filtered_by_end_time"] += filtered_by_end

            df = base_df
            available = len(df)
            stats["observations_available"] += available
            if df.empty:
                logging.warning(
                    "No new data for %s after filtering; skipping.", col
                )
                stats["per_datastream"][str(col)] = {
                    "available": 0,
                    "loaded": 0,
                    "skipped": 0,
                }
                continue

            stats["datastreams_available"] += 1
            df = df.rename(columns={"timestamp": "phenomenon_time", "value": "result"})

            loaded = 0
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
                    loaded += len(chunk)
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

            stats["observations_loaded"] += loaded
            stats["observations_skipped"] += max(available - loaded, 0)
            if loaded > 0:
                stats["datastreams_loaded"] += 1
            stats["per_datastream"][str(col)] = {
                "available": available,
                "loaded": loaded,
                "skipped": max(available - loaded, 0),
            }

        return stats

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
