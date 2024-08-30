import json
import pandas as pd
from typing import Union, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from .base import HydroServerEndpoint
from ..schemas import Datastream

if TYPE_CHECKING:
    from ..service import HydroServer


class DatastreamEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with Datastream entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `Datastream`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'datastreams'`.
    """

    def __init__(self, service) -> None:
        """
        Initialize the DatastreamEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = Datastream
        self._api_route = self._service.api_route
        self._endpoint_route = 'datastreams'

    def get_observations(
            self,
            uid: Union[UUID, str],
            start_time: datetime = None,
            end_time: datetime = None,
            page: int = 1,
            page_size: int = 100000,
            include_quality: bool = False,
            fetch_all: bool = False
    ) -> pd.DataFrame:
        """
        Retrieve observations from a specific Datastream.

        :param uid: The unique identifier of the Datastream.
        :type uid: Union[UUID, str]
        :param start_time: The start time for filtering observations.
        :type start_time: datetime, optional
        :param end_time: The end time for filtering observations.
        :type end_time: datetime, optional
        :param page: The page number to retrieve (used for pagination).
        :type page: int, optional
        :param page_size: The number of observations per page.
        :type page_size: int, optional
        :param include_quality: Whether to include quality information with each observation.
        :type include_quality: bool, optional
        :param fetch_all: Whether to fetch all observations (ignoring pagination).
        :type fetch_all: bool, optional
        :returns: A DataFrame containing the retrieved observations.
        :rtype: pd.DataFrame
        """

        filters = []
        if start_time:
            filters.append(f'phenomenonTime ge {start_time.strftime("%Y-%m-%dT%H:%M:%S%z")}')
        if end_time:
            filters.append(f'phenomenonTime le {end_time.strftime("%Y-%m-%dT%H:%M:%S%z")}')

        if fetch_all:
            page = 1

        observations = []

        while True:
            response = getattr(self._service, '_request')(
                'get', f'{self._api_route}/sensorthings/v1.1/Datastreams(\'{str(uid)}\')/Observations',
                params={
                    '$resultFormat': 'dataArray',
                    '$select': f'phenomenonTime,result{",resultQuality" if include_quality else ""}',
                    '$count': True,
                    '$top': page_size,
                    '$skip': (page - 1) * page_size,
                    '$filter': ' and '.join(filters) if filters else None
                }
            )
            response_content = json.loads(response.content)
            data_array = response_content['value'][0]['dataArray'] if response_content['value'] else []
            observations.extend([[
                obs[0], obs[1],
                obs[2]['qualityCode'] if obs[2]['qualityCode'] else None,
                obs[2]['resultQualifiers'] if obs[2]['resultQualifiers'] else None
            ] if include_quality else [obs[0], obs[1]] for obs in data_array])
            if not fetch_all or len(data_array) < page_size:
                break
            page += 1

        columns = ['timestamp', 'value']
        if include_quality:
            columns.extend(['quality_code', 'result_quality'])

        data_frame = pd.DataFrame(observations, columns=columns)
        data_frame['timestamp'] = pd.to_datetime(data_frame['timestamp'])

        return data_frame

    def upload_observations(
            self,
            uid: Union[UUID, str],
            observations: pd.DataFrame,
    ) -> None:
        """
        Upload observations to a specific Datastream.

        :param uid: The unique identifier of the Datastream.
        :type uid: Union[UUID, str]
        :param observations: A DataFrame containing the observations to upload.
        :type observations: pd.DataFrame
        :returns: None
        """

        data_array = [
            [
                row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S%z'),
                row['value'],
                {
                    'qualityCode': row.get('quality_code', None),
                    'resultQualifiers': row.get('result_qualifiers', []),
                } if 'quality_code' in row or 'result_qualifiers' in row else {}
            ] for _, row in observations.iterrows()
        ]

        getattr(self._service, '_request')(
            'post', f'{self._api_route}/sensorthings/v1.1/CreateObservations',
            headers={'Content-type': 'application/json'},
            data=json.dumps([{
                'Datastream': {'@iot.id': str(uid)},
                'components': ['phenomenonTime', 'result', 'resultQuality'],
                'dataArray': data_array
            }]),
        )
