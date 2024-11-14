import logging
import pandas as pd
from typing import Dict, Optional, Union, Any, List
from .base import Transformer
import json
import jmespath


class JSONTransformer(Transformer):
    def __init__(
        self,
        query_string: str,
        datastream_ids: Dict[str, str],
        timestamp_format: Optional[str] = "ISO8601",
        only_new_data: bool = True,
    ):
        """
        Initializes the JSONTransformer.

        Parameters:
            data_path (str or list of str): JSONPath to the data array containing time series data.
            timestamp_field (str): The key name for the timestamp in each data point.
            datastream_ids (dict): Mapping from JSON field names to datastream IDs.
            timestamp_format (str, optional): The format of the timestamp, if it needs special parsing.
            only_new_data (bool): Flag that filters out data older than datastream.phenomenon_end_time if true.
        """
        self.query_string = query_string
        self.datastream_ids = datastream_ids
        self.timestamp_format = timestamp_format
        self.only_new_data = only_new_data

    @property
    def needs_datastreams(self) -> bool:
        return self.only_new_data

    def transform(self, data_file, datastreams=None):
        """
        Transforms a JSON file-like object into the observations_map format.

        Parameters:
            data_file: File-like object containing JSON data.
            datastreams: Dictionary of datastreams.

        Returns:
            observations_map (dict): Dict mapping datastream IDs to pandas DataFrames.
        """
        json_data = json.load(data_file)
        data_points = self.extract_data_points(json_data)
        if not data_points:
            logging.warning("No data points found in the JSON data.")
            return None

        df = pd.DataFrame(data_points)
        df.dropna(subset=["timestamp"], inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"], format=self.timestamp_format)
        logging.info(f"transformed Pandas data frame: {df}")

        return self.build_observations_map(df, self.datastream_ids, datastreams)

    def extract_data_points(self, json_data: Any) -> Optional[List[dict]]:
        """Extracts data points from the JSON data using the data_path."""
        data_points = jmespath.search(self.query_string, json_data)

        if isinstance(data_points, dict):
            data_points = [data_points]
        return data_points
