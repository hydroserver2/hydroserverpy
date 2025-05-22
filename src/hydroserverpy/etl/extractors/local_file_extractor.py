import logging
from typing import Dict

from .base import Extractor
from ..types import TimeRange


class LocalFileExtractor(Extractor):
    def __init__(self, settings: object):
        if "path" not in settings:
            message = "Missing required setting 'path' in LocalFileExtractor settings."
            logging.error(message)
            raise ValueError(message)
        self.path = settings["path"]

    def prepare_params(self, data_requirements: Dict[str, TimeRange]):
        pass

    def extract(self):
        """
        Opens the file and returns a file-like object.
        """
        try:
            file_handle = open(self.path, "r")
            logging.info(f"Successfully opened file '{self.path}'.")
            return file_handle
        except Exception as e:
            logging.error(f"Error opening file '{self.path}': {e}")
            return None
