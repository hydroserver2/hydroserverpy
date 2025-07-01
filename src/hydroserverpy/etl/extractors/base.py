from abc import abstractmethod
import logging
import pandas as pd
from datetime import datetime

from hydroserverpy.etl.timestamp_parser import TimestampParser


class Extractor:
    def __init__(self, settings: dict):
        self.settings = settings
        self.source_uri = settings["sourceUri"]

    def resolve_placeholder_variables(self, payload, loader):
        logging.info(f"Creating runtime variables...")
        filled = {}
        for var in self.settings.get("placeholderVariables", []):
            name = var["name"]
            var_type = var.get("type", None)

            if var_type == "runTime":
                logging.info(f"Resolving runtime var: {name}")
                if var.get("runTimeValue", None) == "latestObservationTimestamp":
                    value = loader.earliest_begin_date(payload)
                elif var.get("runTimeValue", None) == "jobExecutionTime":
                    value = pd.Timestamp.now(tz="UTC")
            elif var_type == "perPayload":
                logging.info(f"Resolving payload var: {name}")
                payload_vars = payload.get("extractorVariables", {})
                if name not in payload_vars:
                    raise KeyError(f"Missing per-payload variable '{name}'")
                value = payload_vars[name]
            else:
                continue

            if isinstance(value, (datetime, pd.Timestamp)):
                fmt = var.get("timestampFormat", "ISO8601")
                offset = var.get("timestampOffset", "+0000")
                parser = TimestampParser(fmt, offset)
                value = parser.format(value)

            filled[name] = value
        if not filled:
            return self.source_uri
        return self.format_uri(filled)

    def format_uri(self, placeholder_variables):
        try:
            uri = self.source_uri.format(**placeholder_variables)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing placeholder variable: {missing_key}")
        return uri

    @abstractmethod
    def extract(self):
        pass
