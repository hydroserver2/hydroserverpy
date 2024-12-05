import logging
from hydroserverpy.etl.extractors.base import TimeRange
import requests
from io import BytesIO
from typing import Dict
from .base import Extractor


class HTTPExtractor(Extractor):
    def __init__(
        self,
        url: str,
        url_variables: dict = None,
        params: dict = None,
        headers: dict = None,
        auth: tuple = None,
    ):
        self.url = self.format_url(url, url_variables or {})
        self.params = params
        self.headers = headers
        self.auth = auth
        self.start_date = None

    def prepare_params(self, data_requirements: Dict[str, TimeRange]):
        start_times = [
            req["start_time"] for req in data_requirements.values() if req["start_time"]
        ]

        if start_times:
            oldest_start_time = min(start_times).isoformat()
            start_date_key = self.params.pop("start_date_key", None)
            if start_date_key:
                self.params[start_date_key] = oldest_start_time
                logging.info(
                    f"Set start_time to {oldest_start_time} and removed 'start_date_key'"
                )
            else:
                logging.warning("'start_date_key' not found in params.")

    def extract(self):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """
        response = requests.get(
            url=self.url,
            params=self.params,
            headers=self.headers,
            auth=self.auth,
            stream=True,
        )
        response.raise_for_status()
        logging.info(f"Successfully downloaded file from {response.url}")

        data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                data.write(chunk)
        data.seek(0)
        return data

    def format_url(self, url_template, url_variables):
        try:
            url = url_template.format(**url_variables)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing configuration url_variable: {missing_key}")

        return url
