from abc import abstractmethod
import logging
import pandas as pd
from datetime import datetime
from ..etl_configuration import ExtractorConfig, Task
from ..timestamp_parser import TimestampParser


class Extractor:
    def __init__(self, extractor_config: ExtractorConfig):
        self.cfg = extractor_config
        self.runtime_source_uri = None

    def resolve_placeholder_variables(self, task: Task, loader):
        logging.info("Resolving extractor runtime variables...")
        filled = {}
        for placeholder in self.cfg.placeholder_variables:
            name = placeholder.name

            if placeholder.type == "runTime":
                logging.info("Resolving runtime var: %s", name)
                if placeholder.run_time_value == "latestObservationTimestamp":
                    value = loader.earliest_begin_date(task)
                elif placeholder.run_time_value == "jobExecutionTime":
                    value = pd.Timestamp.now(tz="UTC")
            elif placeholder.type == "perTask":
                logging.info("Resolving task var: %s", name)
                if name not in task.extractor_variables:
                    raise KeyError(f"Missing per-task variable '{name}'")
                value = task.extractor_variables[name]
            else:
                continue

            if isinstance(value, (datetime, pd.Timestamp)):
                parser = TimestampParser(placeholder.timestamp)
                value = parser.utc_to_string(value)

            filled[name] = value
        if not filled:
            uri = self.cfg.source_uri
        else:
            uri = self.format_uri(filled)

        self.runtime_source_uri = uri
        logging.info("Resolved runtime source URI: %s", uri)
        return uri

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
