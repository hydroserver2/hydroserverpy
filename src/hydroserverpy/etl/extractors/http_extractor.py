import logging
import requests
from io import BytesIO

from ..etl_configuration import Task
from .base import Extractor, ExtractorConfig


class HTTPExtractor(Extractor):
    def __init__(self, settings: ExtractorConfig):
        super().__init__(settings)

    def extract(self, task: Task, loader=None):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """
        url = self.resolve_placeholder_variables(task, loader)
        logging.info("Requesting data from → %s", url)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logging.error("HTTP request failed for %s: %s", url, e)
            raise

        data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                data.write(chunk)
        data.seek(0)
        return data
