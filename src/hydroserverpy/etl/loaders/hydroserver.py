import logging
import traceback
import pandas as pd
from typing import Union, Optional
from pydantic import ConfigDict
from datetime import datetime
from hydroserverpy import HydroServer
from .base import Loader, ETLLoaderResult, ETLTargetResult
from ..exceptions import ETLError


logger = logging.getLogger(__name__)


class HydroServerLoader(Loader):
    client: HydroServer
    chunk_size: int = 5000

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def load(
        self,
        payload: pd.DataFrame,
        **kwargs
    ) -> ETLLoaderResult:
        """
        Load observations from a DataFrame to corresponding HydroServer datastreams.
        """

        datastreams = {}
        missing_datastreams = []

        for column in payload.columns.difference(["timestamp"]):
            try:
                datastreams[column] = self.client.datastreams.get(column)
            except Exception as e:
                if str(e).startswith("404"):
                    missing_datastreams.append(column)
                else:
                    raise ETLError(
                        f"The HydroServer data loader could not find a destination datastream "
                        f"with ID '{column}'. "
                        f"Ensure the HydroServer connection is configured correctly "
                        f"and is authorized to access the datastream."
                    ) from e

        if missing_datastreams:
            raise ETLError(
                f"The HydroServer data loader could not find one or more destination datastreams. "                
                f"Ensure the HydroServer connection is configured correctly, "
                f"all destination datastreams exist on the configured HydroServer instance, "
                f"and the provided connection is authorized to access the datastreams. "
                f"Missing datastream IDs: {', '.join(sorted(missing_datastreams))}."
            )

        earliest_phenomenon_end_time = min(
            (
                datastream.phenomenon_end_time for datastream in datastreams.values()
                if datastream.phenomenon_end_time is not None
            ), default=None,
        )

        if earliest_phenomenon_end_time is not None:
            observations_df = payload[payload["timestamp"] > earliest_phenomenon_end_time]
        else:
            observations_df = payload

        etl_results = ETLLoaderResult()

        for column, datastream in datastreams.items():
            etl_results.target_results[column] = ETLTargetResult(
                target_identifier=column,
            )
            datastream_df = (
                observations_df[["timestamp", column]]
                .rename(columns={column: "value"})
                .dropna(subset=["value"])
            )

            if datastream.phenomenon_end_time is not None:
                datastream_df = datastream_df.loc[datastream_df["timestamp"] > datastream.phenomenon_end_time]

            if datastream_df.empty:
                etl_results.skipped_count += 1
                etl_results.target_results[column].status = "skipped"
                continue

            datastream_observations_to_load = len(datastream_df)

            logger.info(
                "Uploading %s observation(s) to datastream %s (%s chunk(s), chunk_size=%s)",
                datastream_observations_to_load,
                column,
                (datastream_observations_to_load + self.chunk_size - 1) // self.chunk_size,
                self.chunk_size,
            )

            for start_idx in range(0, datastream_observations_to_load, self.chunk_size):
                end_idx = min(start_idx + self.chunk_size, datastream_observations_to_load)
                chunk = datastream_df.iloc[start_idx:end_idx]

                try:
                    self.client.datastreams.load_observations(
                        uid=datastream.uid, observations=chunk
                    )
                    etl_results.target_results[column].values_loaded += len(chunk)
                except Exception as e:
                    etl_results.target_results[column].status = "failed"
                    etl_results.target_results[column].error = str(e)
                    etl_results.target_results[column].traceback = traceback.format_exc()
                    break

            if not etl_results.target_results[column].values_loaded > 0:
                etl_results.target_results[column].status = "skipped"

            if etl_results.target_results[column].status not in ["skipped", "failed"]:
                etl_results.target_results[column].status = "success"

        etl_results.aggregate_results()

        return etl_results

    def target_loaded_through(
        self,
        target_identifier: Union[str, int]
    ) -> Optional[datetime]:
        """
        Retrieve the timestamp through which data is loaded for a given HydroServer datastream.
        """

        try:
            datastream = self.client.datastreams.get(target_identifier)
        except Exception as e:
            if str(e).startswith("404"):
                raise ETLError(
                    f"The HydroServer data loader could not find a destination datastream "
                    f"with ID '{target_identifier}'. "
                    f"Ensure the HydroServer connection is configured correctly "
                    f"and is authorized to access the datastream."
                ) from e
            else:
                raise ETLError(
                    f"The HydroServer data loader failed to retrieve a destination datastream "
                    f"with ID '{target_identifier}'. "
                    f"Ensure the HydroServer connection is configured correctly "
                    f"and is authorized to access the datastream."
                ) from e

        return datastream.phenomenon_end_time
