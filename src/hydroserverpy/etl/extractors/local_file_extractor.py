import logging
from .base import Extractor
from ..etl_configuration import ExtractorConfig


class LocalFileExtractor(Extractor):
    def __init__(self, extractor_config: ExtractorConfig):
        super().__init__(extractor_config)

    def extract(self, task=None, loader=None):
        """
        Opens the file and returns a file-like object.
        """
        path = (
            self.resolve_placeholder_variables(task, loader)
            if task is not None
            else self.cfg.source_uri
        )
        try:
            file_handle = open(path, "r")
            logging.info("Successfully opened file '%s'.", path)
            return file_handle
        except Exception as e:
            logging.error("Error opening file '%s': %s", path, e)
            return None
