import logging
import requests
from io import BytesIO

from ..etl_configuration import Payload
from .base import Extractor, ExtractorConfig


class HTTPExtractor(Extractor):
    def __init__(self, settings: ExtractorConfig):
        super().__init__(settings)

    def extract(self, payload: Payload, loader=None):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """
        url = self.resolve_placeholder_variables(payload, loader)
        logging.info(f"Requesting data from → {url}")

        response = requests.get(url)
        response.raise_for_status()

        data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                data.write(chunk)
        data.seek(0)
        return data
