import logging
from hydroserverpy.etl.types import TimeRange
import requests
from io import BytesIO
from typing import Dict
from .base import Extractor


class HTTPExtractor(Extractor):
    def __init__(self, settings: object):
        self.url = settings["urlTemplate"]
        # self.url = self.format_url(url, url_variables or {})
        # self.params = settings.get('params', )
        # self.headers = headers
        # self.auth = auth

    def prepare_params(self, data_requirements: Dict[str, TimeRange]):
        pass
        # TODO: Uncomment this once url templates work on in the Data Management App
        # start_times = [
        #     req["start_time"] for req in data_requirements.values() if req["start_time"]
        # ]

        # if start_times:
        #     oldest_start_time = min(start_times)
        #     start_time_key = self.params.pop("start_time_key", None)
        #     if start_time_key:
        #         self.params[start_time_key] = oldest_start_time
        #         logging.info(
        #             f"Set start_time to {oldest_start_time} and removed 'start_time_key'"
        #         )
        #     else:
        #         logging.warning("'start_time_key' not found in params.")

        # end_times = [
        #     req["end_time"] for req in data_requirements.values() if req["end_time"]
        # ]

        # if end_times:
        #     newest_end_time = max(end_times)
        #     end_time_key = self.params.pop("end_time_key", None)
        #     if end_time_key:
        #         self.params[end_time_key] = newest_end_time
        #         logging.info(
        #             f"Set end_time to {newest_end_time} and removed 'end_time_key'"
        #         )
        #     else:
        #         logging.warning("'end_time_key' not found in params.")

    def extract(self):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """

        logging.info(f"Requesting data from → {self.url}")

        # endpoints = [
        #     "https://httpbin.org/get",
        #     "https://jsonplaceholder.typicode.com/posts/1",
        #     "https://api.github.com",
        #     "https://api.ipify.org?format=json",
        #     "https://www.python.org/",
        #     "https://waterservices.usgs.gov/nwis/iv/?&format=json&sites=01646500&parameterCd=00060",
        #     "https://datahub.io/core/country-list/r/data.csv",
        #     "https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv",
        #     # "https://rain-flow.slco.org/export/file/?delimiter=comma&site_id=68&data_start=2025-04-09&data_end=2025-05-09&device_id=2",
        #     # "https://rain-flow.slco.org/export/file/?mime=txt&delimiter=comma&site_id=68&data_start=2025-05-09%2000:00:00&data_end=2025-05-09%2023:59:59&device_id=2"
        # ]
        # for url in endpoints:
        #     try:
        #         r = requests.get(url, timeout=10)
        #         print(f"{url:50} → {r.status_code}")
        #     except Exception as e:
        #         print(f"{url:50} → ERROR: {e}")

        try:
            response = requests.get(self.url)
        except Exception as e:
            logging.error(f"Failed to fetch {repr(self.url)}: {e}")
            raise

        logging.info(f"Received response")

        data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                data.write(chunk)
        data.seek(0)
        return data

    @staticmethod
    def format_url(url_template, url_variables):
        try:
            url = url_template.format(**url_variables)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing configuration url_variable: {missing_key}")

        return url
