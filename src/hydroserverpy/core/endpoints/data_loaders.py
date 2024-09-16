import json
from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.endpoints.data_sources import DataSourceEndpoint
from hydroserverpy.core.schemas import DataLoader, DataSource

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


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

    def list(self) -> List[DataLoader]:
        """
        Retrieve a collection of data loaders owned by the logged-in user.
        """

        return super()._get()

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> DataLoader:
        """
        Retrieve a data loader owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=DataLoader)
    def create(self, **kwargs) -> DataLoader:
        """
        Create a new data loader in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=DataLoader, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> DataLoader:
        """
        Update an existing data loader in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing data loader in HydroServer.
        """

        super()._delete(uid=uid)

    def list_data_sources(self, uid: Union[UUID, str]) -> List[DataSource]:
        """
        Retrieve a list of data source entities associated with a specific data loader.

        :param uid: The unique identifier of the data loader.
        :type uid: Union[UUID, str]
        :returns: A list of data sour instances associated with the data loader.
        :rtype: List[DataSource]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/data-sources'
        )

        endpoint = DataSourceEndpoint(self._service)

        return [
            DataSource(_endpoint=endpoint, _uid=UUID(str(entity.pop('id'))), **entity)
            for entity in json.loads(response.content)
        ]
