from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import SensorThingsService
from hydroserverpy.api.models import ObservedProperty


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ObservedPropertyService(SensorThingsService):
    def __init__(self, connection: "HydroServer"):
        self._model = ObservedProperty
        self._api_route = "api/data"
        self._endpoint_route = "observed-properties"
        self._sta_route = "api/sensorthings/v1.1/ObservedProperties"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> List["ObservedProperty"]:
        """Fetch a collection of observed properties."""

        params = {"$top": page_size, "$skip": page_size * (page - 1)}

        if workspace:
            params["$filter"] = (
                f"properties/workspace/id eq '{str(getattr(workspace, 'uid', workspace))}'"
            )

        return super()._list(params=params)

    def get(
        self, uid: Union[UUID, str], fetch_by_datastream_uid: bool = False
    ) -> "ObservedProperty":
        """Get an observed property by ID."""

        return self._get(
            uid=str(uid),
            path=(
                f"api/sensorthings/v1.1/Datastreams('{str(uid)}')/ObservedProperty"
                if fetch_by_datastream_uid
                else None
            ),
        )

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
