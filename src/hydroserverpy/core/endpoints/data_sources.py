import json
from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.endpoints.datastreams import DatastreamEndpoint
from hydroserverpy.core.schemas import DataSource, Datastream

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


class DataSourceEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with data source entities in the HydroServer service.

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

    def list(self) -> List[DataSource]:
        """
        Retrieve a collection of data sources owned by the logged-in user.
        """

        return super()._get()

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> DataSource:
        """
        Retrieve a data source owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=DataSource)
    def create(self, **kwargs) -> DataSource:
        """
        Create a new data source in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=DataSource, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> DataSource:
        """
        Update an existing data source in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing data source in HydroServer.
        """

        super()._delete(uid=uid)

    def list_datastreams(self, uid: Union[UUID, str]) -> List[Datastream]:
        """
        Retrieve a list of datastream entities associated with a specific data source.

        :param uid: The unique identifier of the data source.
        :type uid: Union[UUID, str]
        :returns: A list of datastream instances associated with the data source.
        :rtype: List[Datastream]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/datastreams'
        )

        endpoint = DatastreamEndpoint(self._service)

        return [
            Datastream(_endpoint=endpoint, _uid=entity.pop('id'), **entity)
            for entity in json.loads(response.content)
        ]
