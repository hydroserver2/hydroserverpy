import logging
import pandas as pd
from typing import Optional, Any, List
from .base import Transformer
import json
import jmespath
from ..etl_configuration import TransformerConfig, SourceTargetMapping


class JSONTransformer(Transformer):
    def __init__(self, transformer_config: TransformerConfig):
        super().__init__(transformer_config)
        self.jmespath = transformer_config.jmespath

    def transform(self, data_file, mappings: List[SourceTargetMapping]):
        """
        Transforms a JSON file-like object into the standard Pandas dataframe format.
        Since JMESPath can natively rename column names, the assumption is the timestamp column
        is always named 'timestamp' for JSON data or converted to 'timestamp' in the JMESPath query.

        Parameters:
            data_file: File-like object containing JSON data.

        Returns:
            pd.DataFrame: pandas DataFrames in the format pd.Timestamp, datastream_id_1, datastream_id_2, ...
        """
        if data_file is None:
            raise TypeError(
                "JSONTransformer received None; expected file-like, bytes, or str"
            )

        json_data = json.load(data_file)
        data_points = self.extract_data_points(json_data)
        if not data_points:
            logging.warning("No data points found in the JSON data.")
            return None

        df = pd.DataFrame(data_points)

        return self.standardize_dataframe(df, mappings)

    def extract_data_points(self, json_data: Any) -> Optional[List[dict]]:
        """Extracts data points from the JSON data using the data_path."""
        data_points = jmespath.search(self.jmespath, json_data)

        if isinstance(data_points, dict):
            data_points = [data_points]
        return data_points
