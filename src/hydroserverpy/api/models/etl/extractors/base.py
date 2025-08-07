from abc import abstractmethod
import logging
import pandas as pd
from datetime import datetime
from ..etl_configuration import ExtractorConfig, Payload
from ..timestamp_parser import TimestampParser


class Extractor:
    def __init__(self, extractor_config: ExtractorConfig):
        self.cfg = extractor_config

    def resolve_placeholder_variables(self, payload: Payload, loader):
        logging.info(f"Creating runtime variables...")
        filled = {}
        for placeholder in self.cfg.placeholder_variables:
            name = placeholder.name

            if placeholder.type == "runTime":
                logging.info(f"Resolving runtime var: {name}")
                if placeholder.run_time_value == "latestObservationTimestamp":
                    value = loader.earliest_begin_date(payload)
                elif placeholder.run_time_value == "jobExecutionTime":
                    value = pd.Timestamp.now(tz="UTC")
            elif placeholder.type == "perPayload":
                logging.info(f"Resolving payload var: {name}")
                if name not in payload.extractor_variables:
                    raise KeyError(f"Missing per-payload variable '{name}'")
                value = payload.extractor_variables[name]
            else:
                continue

            if isinstance(value, (datetime, pd.Timestamp)):
                parser = TimestampParser(placeholder.timestamp)
                value = parser.utc_to_string(value)

            filled[name] = value
        if not filled:
            return self.cfg.source_uri
        return self.format_uri(filled)

    def format_uri(self, placeholder_variables):
        try:
            uri = self.cfg.source_uri.format(**placeholder_variables)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing placeholder variable: {missing_key}")
        return uri

    @abstractmethod
    def extract(self):
        pass
