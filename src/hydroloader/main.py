import requests
import yaml
import json
import csv
from pydantic import AnyHttpUrl, conint
from datetime import datetime
from typing import Tuple, Union, Optional
from hydroloader.models import HydroLoaderConf, HydroLoaderDatastream


class HydroLoader:

    client: requests.Session
    service: Union[AnyHttpUrl, str]
    conf: HydroLoaderConf

    datastreams: dict[str, HydroLoaderDatastream]
    chunk_size: conint(gt=0) = 10000

    timestamp_column_index: Optional[conint(gt=0)]
    datastream_column_indexes: dict[Union[str, int], int]
    observation_bodies: dict[str, list[list[str]]]

    def __init__(
            self,
            conf: Union[str, HydroLoaderConf],
            auth: Tuple[str, str],
            service: Union[AnyHttpUrl, str] = 'http://127.0.0.1:8000/sensorthings/v1.1',
            chunk_size: conint(gt=0) = 10000
    ):
        self.client = requests.Session()
        self.client.auth = auth
        self.service = service

        self.datastreams = {}
        self.chunk_size = chunk_size

        self.datastream_column_indexes = {}
        self.observation_bodies = {}

        if isinstance(conf, str):
            with open(conf, 'r') as conf_file:
                self.conf = HydroLoaderConf.parse_obj(yaml.safe_load(conf_file))
        else:
            self.conf = conf

    def get_datastreams(self):
        """
        The get_datastreams function is used to retrieve datastreams from HydroServer SensorThings API.
        The function takes no arguments and returns a dictionary of HydroLoaderDatastream objects based on the
        datastream IDs in the conf file.

        :param self: Bind the method to an object
        :return: A dictionary of datastreams
        """

        for datastream in self.conf.datastreams:
            request_url = f'{self.service}/Datastreams({datastream.datastream_id})'
            raw_response = self.client.get(request_url)
            response = json.loads(raw_response.content)
            self.datastreams[str(datastream.datastream_id)] = HydroLoaderDatastream(
                id=response['@iot.id'],
                value_count=response['properties']['valueCount'],
                result_time=datetime.strptime(
                    response['resultTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                ) if response['resultTime'] else None,
                phenomenon_time=datetime.strptime(
                    response['phenomenonTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                ) if response['phenomenonTime'] else None
            )

        return self.datastreams

    def sync_datastreams(self):
        """
        The sync_datastreams function is the main method of HydroLoader. It uses the loaded conf file to parse CSV files
        for observations, compares them the data that has already been loaded, and posts batches of observations to the
        HydroServer SensorThings API to bring HydroServer's data store up-to-date with the file data.

        :param self: Bind the method to the object
        :return: The responses returned from the HydroServer SensorThings API.
        """

        if len(self.datastreams.keys()) == 0:
            self.get_datastreams()

        if not self.conf.file_access.path:
            return

        with open(self.conf.file_access.path) as data_file:
            data_reader = csv.reader(data_file, delimiter=self.conf.file_access.delimiter)
            for i, row in enumerate(data_reader):
                self.parse_data_file_row(i + 1, row)
                if i > 0 and i % self.chunk_size == 0:
                    self.post_observations()
            self.post_observations()

    def post_observations(self):
        """
        The post_observations function takes the observation_bodies dictionary and posts it to the HydroServer
        SensorThings API Observations endpoint. Each request body contains a batch of observations associated with a
        single datastream.

        :param self: Represent the instance of the class
        :return: The response of the client
        """

        for datastream_id, observation_body in self.observation_bodies.items():
            request_url = f'{self.service}/Observations'
            request_body = [{
                'Datastream': {
                    '@iot.id': str(datastream_id)
                },
                'components': [
                    'resultTime', 'result'
                ],
                'dataArray': observation_body
            }]
            response = self.client.post(
                request_url,
                json=request_body
            )
            print(response)

        self.observation_bodies = {}

    def parse_data_file_row(self, index, row):
        """
        The parse_data_file_row function is used to parse the data file row by row. The function takes in two
        arguments: index and row. The index argument is the current line number of the data file, and it's used to
        determine if we are at a header or not (if so, then we need to determine the column index for each named
        column). The second argument is a list containing all of the values for each column on that particular line. If
        this isn't a header, then we check if there are any observations with timestamps later than the latest
        timestamp for the associated datastream; if so, then add them into our observation_bodies to be posted.

        :param self: Refer to the object itself
        :param index: Keep track of the row number in the file
        :param row: Access the row of data in the csv file
        :return: A list of datetime and value pairs for each datastream
        """

        if index == self.conf.file_access.header_row:
            self.datastream_column_indexes = {
                datastream.column: row.index(datastream.column)
                if isinstance(datastream.column, str) else datastream.column
                for datastream in self.conf.datastreams
            }
            self.timestamp_column_index = row.index(self.conf.file_timestamp.column) \
                if isinstance(self.conf.file_timestamp.column, str) else self.conf.file_timestamp.column

        if index < self.conf.file_access.data_start_row:
            return

        timestamp = datetime.strptime(
            row[self.timestamp_column_index],
            self.conf.file_timestamp.format
        )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=self.conf.file_timestamp.offset)

        for datastream in self.conf.datastreams:
            ds_timestamp = self.datastreams[str(datastream.datastream_id)].result_time

            if ds_timestamp is None or timestamp > ds_timestamp:
                if str(datastream.datastream_id) not in self.observation_bodies.keys():
                    self.observation_bodies[str(datastream.datastream_id)] = []

                self.observation_bodies[str(datastream.datastream_id)].append([
                    timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), row[self.datastream_column_indexes[datastream.column]]
                ])


hl = HydroLoader(
    conf='/Users/klippold/HydroLoader/LRO1.yaml',
    auth=('test', 'test'),
    service='http://ciroh-his-dev.us-east-1.elasticbeanstalk.com/sensorthings/v1.1'
)

hl.sync_datastreams()
