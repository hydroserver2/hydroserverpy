from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import Unit


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class UnitService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Unit
        self._api_route = "api/data"
        self._endpoint_route = "units"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
    ) -> List["Unit"]:
        """Fetch a collection of units."""

        workspace_id = getattr(workspace, "uid", workspace)
        workspace_id = str(workspace_id) if workspace_id else None

        return super()._list(
            params={"workspace_id": workspace_id} if workspace_id else {},
        )

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
