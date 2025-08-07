import logging
from .base import Extractor
from ..etl_configuration import ExtractorConfig


class LocalFileExtractor(Extractor):
    def __init__(self, extractor_config: ExtractorConfig):
        super().__init__(extractor_config)

    def extract(self):
        """
        Opens the file and returns a file-like object.
        """
        try:
            file_handle = open(self.cfg.source_uri, "r")
            logging.info(f"Successfully opened file '{self.cfg.source_uri}'.")
            return file_handle
        except Exception as e:
            logging.error(f"Error opening file '{self.cfg.source_uri}': {e}")
            return None
