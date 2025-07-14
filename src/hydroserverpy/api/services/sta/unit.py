from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import Unit, UnitCollection


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Thing, Datastream


class UnitService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Unit
        self._collection_model = UnitCollection
        self._api_route = "api/data"
        self._endpoint_route = "units"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        datastream: Optional[Union["Datastream", UUID, str]] = None,
        unit_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["Unit"]:
        """Fetch a collection of units."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))
        if thing is not None:
            params["thing"] = str(getattr(thing, "uid", thing))
        if datastream is not None:
            params["datastream"] = str(getattr(datastream, "uid", datastream))
        if unit_type is not None:
            params["unit_type"] = unit_type

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(self, uid: Union[UUID, str]) -> "Unit":
        """Get a unit by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        name: str,
        symbol: str,
        definition: str,
        unit_type: str,
    ) -> "Unit":
        """Create a new unit."""

        kwargs = {
            "name": name,
            "symbol": symbol,
            "definition": definition,
            "type": unit_type,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        symbol: str = ...,
        definition: str = ...,
        unit_type: str = ...,
    ) -> "Unit":
        """Update a unit."""

        kwargs = {
            "name": name,
            "symbol": symbol,
            "definition": definition,
            "type": unit_type,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a unit."""

        super()._delete(uid=str(uid))
