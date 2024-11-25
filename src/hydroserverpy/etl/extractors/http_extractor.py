import logging
import requests
from io import BytesIO
from typing import Dict, Any
import pandas as pd


class HTTPExtractor:
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

    @property
    def needs_datastreams(self) -> bool:
        """
        Some apis have a 'start_date_key' query param. If so, we'll check the datastreams
        for their most recent observations and set 'start_date_key' to the oldest of
        those timestamps.
        """

        return "start_date_key" in self.params

    def extract(self, datastreams: Dict[str, Any] = None):
        """
        Downloads the file from the HTTP/HTTPS server and returns a file-like object.
        """
        if self.needs_datastreams:
            self.set_start_date(datastreams)
            logging.info(f"updated params: {self.params}")

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

    def set_start_date(self, datastreams: Dict[str, Any]):
        """
        Updates self.params based on the datastreams provided.

        Parameters:
            datastreams (dict): Dictionary of datastreams keyed by datastream ID.
        """

        # Extract the earliest phenomenon_end_time among the datastreams
        start_dates = [
            pd.to_datetime(ds.phenomenon_end_time)
            for ds in datastreams.values()
            if ds.phenomenon_end_time
        ]

        earliest_start_date = (
            min(start_dates) if start_dates else pd.Timestamp("1970-01-01T00:00:00Z")
        )

        self.params["start_date_key"] = earliest_start_date.isoformat()

    def format_url(self, url_template, url_variables):
        try:
            url = url_template.format(**url_variables)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing configuration url_variable: {missing_key}")

        return url
