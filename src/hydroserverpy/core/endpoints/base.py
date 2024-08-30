import json
from uuid import UUID
from typing import TYPE_CHECKING, Type, Union, List

if TYPE_CHECKING:
    from ..schemas.base import HydroServerCoreModel
    from ..service import HydroServer


class HydroServerEndpoint:
    """
    A base class for interacting with specific API endpoints within a HydroServer service.

    :ivar _model: The model class associated with this endpoint.
    :ivar _api_route: The base route of the API.
    :ivar _endpoint_route: The specific route of the endpoint.
    """

    _model: Type['HydroServerCoreModel']
    _api_route: str
    _endpoint_route: str

    def __init__(self, service: 'HydroServer') -> None:
        """
        Initialize the HydroServerEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        self._service = service

    def list(self) -> List['HydroServerCoreModel']:
        """
        Retrieve a list of entities from the endpoint.

        :returns: A list of model instances representing the entities.
        :rtype: List[HydroServerCoreModel]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}'
        )

        return [
            self._model(_endpoint=self, _uid=entity.pop('id'), **entity)
            for entity in json.loads(response.content)
        ]

    def get(self, uid: Union[UUID, str]) -> 'HydroServerCoreModel':
        """
        Retrieve a single entity from the endpoint by its unique identifier.

        :param uid: The unique identifier of the entity to retrieve.
        :type uid: Union[UUID, str]
        :returns: A model instance representing the entity.
        :rtype: HydroServerCoreModel
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}'
        )
        entity = json.loads(response.content)

        return self._model(_endpoint=self, _uid=entity.pop('id'), **entity)

    def create(self, **kwargs) -> 'HydroServerCoreModel':
        """
        Create a new entity in the endpoint.

        :param kwargs: The attributes to set on the new entity.
        :returns: A model instance representing the newly created entity.
        :rtype: HydroServerCoreModel
        """

        response = getattr(self._service, '_request')(
            'post', f'{self._api_route}/data/{self._endpoint_route}',
            headers={'Content-type': 'application/json'},
            data=self._model(_endpoint=self, **kwargs).json(exclude_unset=True, by_alias=True),
        )
        entity = json.loads(response.content)

        return self._model(_endpoint=self, _uid=entity.pop('id'), **entity)

    def update(self, uid: Union[UUID, str], **kwargs) -> 'HydroServerCoreModel':
        """
        Update an existing entity in the endpoint.

        :param uid: The unique identifier of the entity to update.
        :type uid: Union[UUID, str]
        :param kwargs: The attributes to update on the entity.
        :returns: A model instance representing the updated entity.
        :rtype: HydroServerCoreModel
        """

        response = getattr(self._service, '_request')(
            'patch', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}',
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                self._model.model_fields[key].serialization_alias: value
                for key, value in kwargs.items()
            })
        )
        entity = json.loads(response.content)

        return self._model(_endpoint=self, _uid=entity.pop('id'), **entity)

    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an entity from the endpoint by its unique identifier.

        :param uid: The unique identifier of the entity to delete.
        :type uid: Union[UUID, str]
        :returns: None
        """

        getattr(self._service, '_request')(
            'delete', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}',
        )
