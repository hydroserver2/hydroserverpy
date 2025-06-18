import logging
from .base import Extractor


class LocalFileExtractor(Extractor):
    def __init__(self, settings: object):
        super().__init__(settings)

    def extract(self):
        """
        Opens the file and returns a file-like object.
        """
        try:
            file_handle = open(self.source_uri, "r")
            logging.info(f"Successfully opened file '{self.source_uri}'.")
            return file_handle
        except Exception as e:
            logging.error(f"Error opening file '{self.source_uri}': {e}")
            return None
