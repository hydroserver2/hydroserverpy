import json
from uuid import UUID
from typing import TYPE_CHECKING, Type, Union, List, TypeVar, Optional

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.core.schemas.base import HydroServerCoreModel

    HydroServerModelType = TypeVar("HydroServerModelType", bound=HydroServerCoreModel)


def expand_docstring(
    model: Optional[Type["HydroServerCoreModel"]] = None, include_uid: bool = False
):
    def decorator(func):
        docstring = func.__doc__
        if model is not None or include_uid is True:
            docstring += "\n"
        if include_uid is True:
            docstring += f":param uid: The entity ID.\n"
            docstring += f":type uid: Union[UUID, str]\n"
        if model is not None:
            for field_name, field in model.model_fields.items():
                docstring += f":param {field_name}: {field.description}\n"
                docstring += f':type {field_name}: {getattr(field.annotation, "__name__", field.annotation)}\n'
        func.__doc__ = docstring
        return func

    return decorator


class HydroServerEndpoint:
    """
    A base class for interacting with specific API endpoints within a HydroServer service.

    :ivar _model: The model class associated with this endpoint.
    :ivar _api_route: The base route of the API.
    :ivar _endpoint_route: The specific route of the endpoint.
    """

    _model: Type["HydroServerCoreModel"]
    _api_route: str
    _endpoint_route: str

    def __init__(self, service: "HydroServer") -> None:
        """
        Initialize the HydroServerEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        self._service = service

    def _get(
        self, uid: Optional[Union[UUID, str]] = None, params: dict = None
    ) -> Union[List["HydroServerModelType"], "HydroServerModelType"]:
        """
        Fetch an entity collection or single entity from a HydroServer endpoint.

        :param uid: The unique identifier of the entity to retrieve.
        :type uid: Optional[Union[UUID, str]]
        :returns: A model instance representing the entity.
        :rtype: HydroServerCoreModel
        """

        if params is None:
            params = {}

        path = f'{self._api_route}/data/{self._endpoint_route}{"/" + str(uid) if uid else ""}'
        response = getattr(self._service, "_request")("get", path, params=params)

        if uid:
            entity = json.loads(response.content)
            result = self._model(
                _endpoint=self, _uid=UUID(str(entity.pop("id"))), **entity
            )
        else:
            result = [
                self._model(_endpoint=self, _uid=UUID(str(entity.pop("id"))), **entity)
                for entity in json.loads(response.content)
            ]

        return result

    def _post(self, **kwargs) -> "HydroServerModelType":
        """
        Create a new entity using the endpoint.

        :param kwargs: The attributes to set on the new entity.
        :returns: A model instance representing the newly created entity.
        :rtype: HydroServerModelType
        """

        response = getattr(self._service, "_request")(
            "post",
            f"{self._api_route}/data/{self._endpoint_route}",
            headers={"Content-type": "application/json"},
            data=self._model(_endpoint=self, **kwargs).json(
                exclude_unset=True, by_alias=True
            ),
        )
        entity = json.loads(response.content)

        return self._model(_endpoint=self, _uid=UUID(str(entity.pop("id"))), **entity)

    def _patch(self, uid: Union[UUID, str], **kwargs) -> "HydroServerModelType":
        """
        Update an existing entity in the endpoint.

        :param uid: The unique identifier of the entity to update.
        :type uid: Union[UUID, str]
        :param kwargs: The attributes to update on the entity.
        :returns: A model instance representing the updated entity.
        :rtype: HydroServerModelType
        """

        response = getattr(self._service, "_request")(
            "patch",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}",
            headers={"Content-type": "application/json"},
            data=json.dumps(
                {
                    self._model.model_fields[key].serialization_alias: value
                    for key, value in kwargs.items()
                },
                default=str,
            ),
        )
        entity = json.loads(response.content)

        return self._model(_endpoint=self, _uid=UUID(str(entity.pop("id"))), **entity)

    def _delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an entity from the endpoint by its unique identifier.

        :param uid: The unique identifier of the entity to delete.
        :type uid: Union[UUID, str]
        :returns: None
        """

        getattr(self._service, "_request")(
            "delete",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}",
        )
