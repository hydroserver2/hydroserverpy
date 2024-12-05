import logging
from .base import Extractor


class LocalFileExtractor(Extractor):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract(self):
        """
        Opens the file and returns a file-like object.
        """
        try:
            file_handle = open(self.filepath, "r")
            logging.info(f"Successfully opened file '{self.filepath}'.")
            return file_handle
        except Exception as e:
            logging.error(f"Error opening file '{self.filepath}': {e}")
            return None
