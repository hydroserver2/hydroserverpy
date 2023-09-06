import requests
import yaml
import json
import csv
import logging
from pydantic import AnyHttpUrl, conint
from datetime import datetime, timezone
from dateutil.parser import isoparse
from typing import Tuple, Union, Optional, Dict, List
from hydroloader.models import HydroLoaderConf, HydroLoaderDatastream, HydroLoaderObservationsResponse
from hydroloader.exceptions import HeaderParsingError, TimestampParsingError


logger = logging.getLogger('hydroloader')
logger.addHandler(logging.NullHandler())


class HydroLoader:

    auth: Tuple[str, str]
    service: Union[AnyHttpUrl, str]
    conf: HydroLoaderConf

    file_result_timestamp: Optional[datetime]
    datastreams: Dict[str, HydroLoaderDatastream]
    chunk_size: conint(gt=0) = 10000

    timestamp_column_index: Optional[conint(gt=0)]
    datastream_column_indexes: Dict[Union[str, int], int]
    observation_bodies: Dict[str, List[List[str]]]

    def __init__(
            self,
            conf: Union[str, HydroLoaderConf],
            auth: Tuple[str, str],
            service: Union[AnyHttpUrl, str] = 'http://127.0.0.1:8000/sensorthings/v1.1',
            chunk_size: conint(gt=0) = 10000
    ):
        self.auth = auth
        self.service = service
        self.timeout = 60

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
            request_url = f'{self.service}/Datastreams({datastream.id})'

            try:
                raw_response = requests.get(request_url, auth=self.auth, timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                logger.error(
                    'Failed to make request to "' + request_url + '" with error: ' + str(e)
                )
                continue

            if raw_response.status_code != 200:
                logger.error(
                    'SensorThings request to "' + request_url + '" failed with status code: ' +
                    str(raw_response.status_code) + ': ' + raw_response.reason
                )
                continue

            try:
                response = json.loads(raw_response.content)
            except ValueError as e:
                logger.error(
                    'Failed to parse SensorThings response from "' + request_url + '" with error: ' + str(e)
                )
                continue

            try:
                if self.datastreams.get(str(datastream.id)):
                    self.datastreams[str(datastream.id)].value_count = response['properties']['valueCount']
                    self.datastreams[str(datastream.id)].result_time = datetime.strptime(
                        response['resultTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                    ) if response.get('resultTime') else None
                    self.datastreams[str(datastream.id)].phenomenon_time = datetime.strptime(
                        response['phenomenonTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                    ) if response.get('phenomenonTime') else None
                else:
                    self.datastreams[str(datastream.id)] = HydroLoaderDatastream(
                        id=response['@iot.id'],
                        valueCount=response['properties']['valueCount'],
                        resultTime=datetime.strptime(
                            response['resultTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                        ) if response.get('resultTime') else None,
                        phenomenonTime=datetime.strptime(
                            response['phenomenonTime'].split('/')[1].replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S%z'
                        ) if response.get('phenomenonTime') else None
                    )
            except (KeyError, ValueError, IndexError) as e:
                logger.error(
                    'Failed to parse SensorThings response body from "' + request_url + '" with error: ' + str(e)
                )
                continue

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
            message = f'No data source file configured.'
            return {
                'data_thru': None,
                'success': True,
                'message': message
            }

        if len(self.conf.datastreams) == 0:
            message = f'No datastreams configured for data source file: {self.conf.file_access.path}'
            return {
                'data_thru': None,
                'success': True,
                'message': message
            }

        message = None

        with open(self.conf.file_access.path) as data_file:
            data_reader = csv.reader(data_file, delimiter=self.conf.file_access.delimiter)
            file_parsing_error = False
            failed_datastreams = []
            for i, row in enumerate(data_reader):
                try:
                    self.parse_data_file_row(i + 1, row)
                except HeaderParsingError as e:
                    message = f'Failed to parse data file headers for "{self.conf.file_access.path}" ' + \
                        f'with error: {str(e)}'
                    logger.error(message)
                    file_parsing_error = True
                    break
                except TimestampParsingError as e:
                    message = f'Failed to parse timestamp on row {i + 1} for "{self.conf.file_access.path}" ' + \
                        f'with error: {str(e)}'
                    logger.error(message)
                    file_parsing_error = True
                    break
                if i > 0 and i % self.chunk_size == 0:
                    responses = self.post_observations(
                        skip_datastreams=failed_datastreams
                    )
                    failed_datastreams = self.handle_post_responses(
                        responses=responses,
                        failed_datastreams=failed_datastreams
                    )
            if not file_parsing_error:
                responses = self.post_observations(
                    skip_datastreams=failed_datastreams
                )
                self.handle_post_responses(
                    responses=responses,
                    failed_datastreams=failed_datastreams
                )

        if not message and len(failed_datastreams) > 0:
            message = 'One or more datastreams failed to sync with HydroServer.'

        return {
            'data_thru': getattr(self, 'file_result_timestamp', None),
            'success': len(failed_datastreams) == 0 and file_parsing_error is False,
            'message': message
        }

    @staticmethod
    def handle_post_responses(responses, failed_datastreams):
        """
        The handle_post_responses function takes a list of responses from SensorThings observations POST requests and
        a list of datastreams that have failed to post observations. It iterates through each response,
        and if the status code is not 201 (created), it logs an error message with information about
        the request URL, chunk start time, chunk end time, status code and reason for failure. If the
        status code is 201 (created), it logs a success message with information about the chunk start time,
        chunk end time and datastream ID. The function returns a set of unique IDs for all failed datastreams.

        :param responses: Store the response from the post request
        :param failed_datastreams: Keep track of the datastreams that failed to post observations
        :return: A set of datastreams that failed to post
        """

        for response in responses:
            if response.status_code != 201:
                logger.error(
                    f'Observations POST request to "{response.request_url}" ' +
                    f'from {response.chunk_start_time} to {response.chunk_end_time} ' +
                    f'failed with error: {str(response.status_code)}: {response.reason}')
                failed_datastreams.append(response.datastream_id)
            else:
                logger.info(
                    f'Posted observations from {response.chunk_start_time} to {response.chunk_end_time} ' +
                    f'for datastream {response.datastream_id}'
                )

        return list(set(failed_datastreams))

    def post_observations(self, skip_datastreams):
        """
        The post_observations function takes the observation_bodies dictionary and posts it to the HydroServer
        SensorThings API Observations endpoint. Each request body contains a batch of observations associated with a
        single datastream.

        :param self: Represent the instance of the class
        :param skip_datastreams: A list of datastreams to skip
        :return: The response of the client
        """

        responses = []

        for datastream_id, observation_body in self.observation_bodies.items():
            chunk_start_time = self.datastreams[datastream_id].chunk_result_start_time
            chunk_end_time = self.datastreams[datastream_id].chunk_result_end_time
            if str(datastream_id) not in skip_datastreams:
                request_url = f'{self.service}/Observations'
                request_body = [{
                    'Datastream': {
                        '@iot.id': str(datastream_id)
                    },
                    'components': [
                        'phenomenonTime', 'result'
                    ],
                    'dataArray': observation_body
                }]
                response = requests.post(
                    request_url,
                    json=request_body,
                    auth=self.auth,
                    timeout=self.timeout
                )
                responses.append(HydroLoaderObservationsResponse(
                    datastream_id=datastream_id,
                    request_url=request_url,
                    status_code=response.status_code,
                    reason=response.reason,
                    chunk_start_time=chunk_start_time.strftime("%Y-%m-%d %H:%M:%S%z"),
                    chunk_end_time=chunk_end_time.strftime("%Y-%m-%d %H:%M:%S%z")
                ))
            else:
                logger.info(
                    f'Skipping observations POST request from ' +
                    f'{chunk_start_time.strftime("%Y-%m-%d %H:%M:%S%z")} to ' +
                    f'{chunk_end_time.strftime("%Y-%m-%d %H:%M:%S%z")} for datastream: ' +
                    f'{str(datastream_id)}, due to previous failed POST request.'
                )
            self.datastreams[datastream_id].chunk_result_start_time = None
            self.datastreams[datastream_id].chunk_result_end_time = None

        self.observation_bodies = {}

        return responses

    def parse_data_file_row(self, index, row):
        """
        The parse_data_file_row function is used to parse the data file row by row. The function takes in two
        arguments: index and row. The index argument is the current line number of the data file, and it's used to
        determine if we are at a header or not (if so, then we need to determine the column index for each named
        column). The second argument is a list containing all the values for each column on that particular line. If
        this isn't a header, then we check if there are any observations with timestamps later than the latest
        timestamp for the associated datastream; if so, then add them into our observation_bodies to be posted.

        :param self: Refer to the object itself
        :param index: Keep track of the row number in the file
        :param row: Access the row of data in the csv file
        :return: A list of datetime and value pairs for each datastream
        """

        if index == self.conf.file_access.header_row or (
                index == self.conf.file_access.data_start_row and not hasattr(self, 'timestamp_column_index')
        ):
            try:
                self.datastream_column_indexes = {
                    datastream.column: row.index(datastream.column)
                    if isinstance(datastream.column, str) else datastream.column - 1
                    for datastream in self.conf.datastreams
                }
                self.timestamp_column_index = row.index(self.conf.file_timestamp.column) \
                    if isinstance(self.conf.file_timestamp.column, str) else self.conf.file_timestamp.column - 1
                if max(self.datastream_column_indexes.values()) > len(row) or self.timestamp_column_index > len(row):
                    raise ValueError
            except ValueError as e:
                raise HeaderParsingError(str(e)) from e

        if index < self.conf.file_access.data_start_row:
            return

        try:
            if self.conf.file_timestamp.format == 'iso':
                timestamp = isoparse(
                    row[self.timestamp_column_index]
                )
            else:
                timestamp = datetime.strptime(
                    row[self.timestamp_column_index],
                    self.conf.file_timestamp.format
                )
        except ValueError as e:
            raise TimestampParsingError(str(e)) from e

        if timestamp.tzinfo is None:
            if not self.conf.file_timestamp.offset:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )
            else:
                try:
                    timestamp = timestamp.replace(
                        tzinfo=datetime.strptime(
                            self.conf.file_timestamp.offset[:-2] + ':' + self.conf.file_timestamp.offset[3:], '%z'
                        ).tzinfo
                    )
                except ValueError as e:
                    raise TimestampParsingError(str(e)) from e

        self.file_result_timestamp = timestamp

        for datastream in [
            ds for ds in self.conf.datastreams if str(ds.id) in self.datastreams.keys()
        ]:
            ds_timestamp = self.datastreams[str(datastream.id)].phenomenon_time

            if not self.datastreams[str(datastream.id)].file_row_start_index:
                if ds_timestamp is None or timestamp > ds_timestamp:
                    self.datastreams[str(datastream.id)].file_row_start_index = index

            if self.datastreams[str(datastream.id)].file_row_start_index and \
                    self.datastreams[str(datastream.id)].file_row_start_index <= index:
                if str(datastream.id) not in self.observation_bodies.keys():
                    self.observation_bodies[str(datastream.id)] = []

                if not self.datastreams[str(datastream.id)].chunk_result_start_time:
                    self.datastreams[str(datastream.id)].chunk_result_start_time = timestamp
                self.datastreams[str(datastream.id)].chunk_result_end_time = timestamp

                self.observation_bodies[str(datastream.id)].append([
                    timestamp.strftime('%Y-%m-%dT%H:%M:%S%z'), row[self.datastream_column_indexes[datastream.column]]
                ])
