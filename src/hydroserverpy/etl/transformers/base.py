from abc import ABC, abstractmethod
import logging
import pandas as pd


class Transformer(ABC):
    @abstractmethod
    def transform(self) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        False

    def build_observations_map(self, df, datastream_ids, datastreams=None):
        observations_map = {}
        for column_name, datastream_id in datastream_ids.items():
            if column_name not in df.columns:
                logging.error(f"Datastream column '{column_name}' not found in file.")
                continue

            observations = df[["timestamp", column_name]].dropna()
            if observations.empty:
                logging.warning(f"No data found for input column {column_name}")
                continue
            observations = observations.rename(columns={column_name: "value"})

            if datastreams:
                datastream = datastreams.get(datastream_id)
                observations = self.filter_out_old_data(datastream, observations)

            if observations is None or observations.empty:
                logging.info(f"No new observations to add for '{datastream_id}'.")
                continue
            observations_map[datastream_id] = observations
        return observations_map

    def filter_out_old_data(self, datastream, observations):
        phenomenon_end_time = datastream.phenomenon_end_time
        if not phenomenon_end_time:
            return observations

        if not isinstance(phenomenon_end_time, pd.Timestamp):
            try:
                phenomenon_end_time = pd.to_datetime(phenomenon_end_time)
            except Exception as e:
                logging.error(
                    f"Invalid phenomenon_end_time for datastream {datastream.id}: {e}"
                )
                return None
        return observations[observations["timestamp"] > phenomenon_end_time]
