import json
from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from .base import HydroServerEndpoint
from ..schemas import DataLoader, DataSource

if TYPE_CHECKING:
    from ..service import HydroServer


class DataLoaderEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with DataLoader entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `DataLoader`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'data-loaders'`.
    """

    def __init__(self, service: 'HydroServer') -> None:
        """
        Initialize the DataLoaderEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = DataLoader
        self._api_route = self._service.api_route
        self._endpoint_route = 'data-loaders'

    def list_data_sources(self, uid: Union[UUID, str]) -> List[DataSource]:
        """
        Retrieve a list of DataSource entities associated with a specific DataLoader.

        :param uid: The unique identifier of the DataLoader.
        :type uid: Union[UUID, str]
        :returns: A list of DataSource instances associated with the DataLoader.
        :rtype: List[DataSource]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/data-sources'
        )

        return [
            DataSource(_endpoint=self, _uid=entity.pop('id'), **entity)
            for entity in json.loads(response.content)
        ]
