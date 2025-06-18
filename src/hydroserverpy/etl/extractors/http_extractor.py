import logging
import requests
from io import BytesIO
from .base import Extractor


class HTTPExtractor(Extractor):
    def __init__(self, settings: dict):
        super().__init__(settings)

    def extract(self, payload, loader=None):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """
        url = self.resolve_placeholder_variables(payload, loader)
        logging.info(f"Requesting data from → {url}")

        try:
            response = requests.get(url)
        except Exception as e:
            logging.error(f"Failed to fetch {url}: {e}")
            raise

        data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                data.write(chunk)
        data.seek(0)
        return data
