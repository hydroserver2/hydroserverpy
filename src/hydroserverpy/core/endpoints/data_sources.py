import json
from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from .base import HydroServerEndpoint
from ..schemas import DataSource, Datastream

if TYPE_CHECKING:
    from ..service import HydroServer


class DataSourceEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with DataSource entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `DataSource`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'data-sources'`.
    """

    def __init__(self, service: 'HydroServer') -> None:
        """
        Initialize the DataSourceEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = DataSource
        self._api_route = self._service.api_route
        self._endpoint_route = 'data-sources'

    def list_datastreams(self, uid: Union[UUID, str]) -> List[Datastream]:
        """
        Retrieve a list of Datastream entities associated with a specific DataSource.

        :param uid: The unique identifier of the DataSource.
        :type uid: Union[UUID, str]
        :returns: A list of Datastream instances associated with the DataSource.
        :rtype: List[Datastream]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/datastreams'
        )
        return [
            Datastream(_endpoint=self, _uid=entity.pop('id'), **entity)
            for entity in json.loads(response.content)
        ]
