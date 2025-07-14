from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import ObservedProperty


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Thing, Datastream


class ObservedPropertyService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = ObservedProperty
        self._api_route = "api/data"
        self._endpoint_route = "observed-properties"
        self._sta_route = "api/sensorthings/v1.1/ObservedProperties"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        datastream: Optional[Union["Datastream", UUID, str]] = None,
        observed_property_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["ObservedProperty"]:
        """Fetch a collection of observed properties."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))
        if thing is not None:
            params["thing"] = str(getattr(thing, "uid", thing))
        if datastream is not None:
            params["datastream"] = str(getattr(datastream, "uid", datastream))
        if observed_property_type is not None:
            params["observed_property_type"] = observed_property_type

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(self, uid: Union[UUID, str]) -> "ObservedProperty":
        """Get an observed property by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        name: str,
        definition: str,
        description: str,
        observed_property_type: str,
        code: str,
        workspace: Union["Workspace", UUID, str],
    ) -> "ObservedProperty":
        """Create a new observed property."""

        kwargs = {
            "name": name,
            "definition": definition,
            "description": description,
            "type": observed_property_type,
            "code": code,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        definition: str = ...,
        description: str = ...,
        observed_property_type: str = ...,
        code: str = ...,
    ) -> "ObservedProperty":
        """Update an observed property."""

        kwargs = {
            "name": name,
            "definition": definition,
            "description": description,
            "type": observed_property_type,
            "code": code,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete an observed property."""

        super()._delete(uid=str(uid))
