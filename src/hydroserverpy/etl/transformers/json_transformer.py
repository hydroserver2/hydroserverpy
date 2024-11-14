import logging
import pandas as pd
from typing import Dict, Optional, Union, Any, List
from .base import Transformer
import json


class JSONTransformer(Transformer):
    def __init__(
        self,
        data_path: Union[str, List[str]],
        timestamp_field: str,
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
        self.data_path = data_path
        self.timestamp_field = timestamp_field
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
        try:
            json_data = json.load(data_file)
        except Exception as e:
            logging.error(f"Error loading JSON data: {e}")
            return None

        data_points = self.extract_data_points(json_data)
        if data_points is None:
            logging.error("No data points found in the JSON data.")
            return None

        try:
            df = pd.DataFrame(data_points)
        except Exception as e:
            logging.error(f"Error converting data points to DataFrame: {e}")
            return None

        if self.timestamp_field not in df.columns:
            logging.error(
                f"Timestamp field '{self.timestamp_field}' not found in data."
            )
            return None

        df["timestamp"] = df[self.timestamp_field].apply(self.parse_timestamp)
        logging.info(f"transformed Pandas data frame: {df}")
        df.dropna(subset=["timestamp"], inplace=True)

        return self.build_observations_map(df, self.datastream_ids, datastreams)

    def extract_data_points(self, json_data: Any) -> Optional[List[dict]]:
        """
        Extracts data points from the JSON data using the data_path.

        Parameters:
            json_data: The loaded JSON data.

        Returns:
            List of data point dictionaries.
        """
        try:
            data_points = [json_data]
            for key in self.data_path:
                temp = []
                if key == "*":
                    # Expand all items in lists
                    for item in data_points:
                        if isinstance(item, list):
                            temp.extend(item)
                        elif isinstance(item, dict):
                            temp.extend(item.values())
                        else:
                            logging.error(
                                f"Unexpected data type {type(item)} encountered."
                            )
                else:
                    # Access by key or index
                    for item in data_points:
                        if isinstance(item, dict):
                            if key in item:
                                temp.append(item[key])
                        elif isinstance(item, list):
                            try:
                                index = int(key)
                                temp.append(item[index])
                            except (ValueError, IndexError):
                                logging.error(f"Invalid index {key} for list.")
                        else:
                            logging.error(
                                f"Unexpected data type {type(item)} encountered."
                            )
                data_points = temp
            return data_points
        except Exception as e:
            logging.error(f"Error extracting data points using data_path: {e}")
            return None

    def parse_timestamp(self, timestamp_str: str) -> Optional[pd.Timestamp]:
        return pd.to_datetime(timestamp_str, format=self.timestamp_format)
