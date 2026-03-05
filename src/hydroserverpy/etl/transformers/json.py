import logging
import json
import jmespath
import pandas as pd
from io import BytesIO, TextIOBase, BufferedIOBase
from typing import Union, TextIO
from pydantic import model_validator
from jmespath.exceptions import JMESPathError
from .base import Transformer, ETLDataMapping
from ..exceptions import ETLError


logger = logging.getLogger(__name__)


class JSONTransformer(Transformer):
    jmespath: str

    @model_validator(mode="after")
    def validate_jmespath(self) -> "JSONTransformer":
        """
        Ensure that the jmespath expression is syntactically correct.
        """

        try:
            jmespath.compile(self.jmespath)
        except JMESPathError as e:
            raise ValueError(
                f"Received an invalid JMESPath expression for the JSON transformer: "
                f"{self.jmespath!r}. "
                f"Error: {str(e)}"
            ) from e

        return self

    def transform(
        self,
        payload: Union[str, TextIO, BytesIO],
        data_mappings: list[ETLDataMapping],
        **kwargs
    ) -> pd.DataFrame:
        """
        Transforms a JSON file-like object into the standard Pandas dataframe format.
        Since JMESPath can natively rename column names, the assumption is the timestamp column
        is always named 'timestamp' for JSON data or converted to 'timestamp' in the JMESPath query.
        """

        if not isinstance(payload, (str, bytes, TextIOBase, BufferedIOBase)):
            raise ETLError(
                f"The JSON transformer received a payload object of type {type(payload).__name__}; "
                "expected one of: str, bytes, TextIO, BytesIO. "
                "Ensure the source system is returning a file-like object."
            )

        try:
            if isinstance(payload, (str, bytes)):
                json_data = json.loads(payload)
            else:
                json_data = json.load(payload)
        except json.JSONDecodeError as e:
            raise ETLError(
                "The JSON transformer received a payload that is not valid JSON. "
                "Ensure the source system is returning properly formatted JSON data."
            ) from e
        except Exception as e:
            raise ETLError(
                "The JSON transformer encountered an unexpected error while parsing the provided payload. "
                "Ensure the source system is returning properly formatted JSON data."
            ) from e

        if not isinstance(json_data, (dict, list)):
            raise ETLError(
                "The JSON transformer received a JSON payload that it cannot evaluate. "
                "The JSON payload must be a dictionary or a list at the top level."
            )

        logger.debug("Loaded JSON payload (type=%s).", type(json_data).__name__)

        try:
            data_points = jmespath.search(self.jmespath, json_data)
        except JMESPathError as e:
            raise ETLError(
                f"The JMESPath expression '{self.jmespath}' provided to the JSON transformer "
                f"could not be evaluated against the JSON payload. "
                f"Verify the expression and the payload structure are correct."
            ) from e

        if data_points is None:
            raise ETLError(
                f"The JMESPath expression '{self.jmespath}' provided to the JSON transformer "
                f"did not match anything in the JSON payload. "
                f"Verify the expression matches the structure of the source data."
            )

        if isinstance(data_points, dict):
            data_points = [data_points]

        # Treat an empty result list as "no data" (not a configuration error).
        # Build an empty frame with the expected columns so standardization can proceed cleanly.
        if len(data_points) == 0:
            df = pd.DataFrame(columns=(
                [self.timestamp_key] + [data_mapping.source_identifier for data_mapping in data_mappings]
            ))
        else:
            df = pd.DataFrame(data_points)

        logger.debug("Extracted %s JSON data point(s).", len(data_points))

        return self.standardize_dataframe(df, data_mappings)
