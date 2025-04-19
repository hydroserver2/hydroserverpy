from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import OrchestrationSystem


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class OrchestrationSystemService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = OrchestrationSystem
        self._api_route = "api/data"
        self._endpoint_route = "orchestration-systems"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
    ) -> List["OrchestrationSystem"]:
        """Fetch a collection of orchestration systems."""

        workspace_id = getattr(workspace, "uid", workspace)
        workspace_id = str(workspace_id) if workspace_id else None

        return super()._list(
            params={"workspace_id": workspace_id} if workspace_id else {},
        )

    def get(self, uid: Union[UUID, str]) -> "OrchestrationSystem":
        """Get an orchestration system by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        name: str,
        orchestration_system_type: str,
    ) -> "OrchestrationSystem":
        """Create a new orchestration system."""

        kwargs = {
            "name": name,
            "type": orchestration_system_type,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        orchestration_system_type: str = ...,
    ) -> "OrchestrationSystem":
        """Update an orchestration system."""

        kwargs = {
            "name": name,
            "type": orchestration_system_type,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete an orchestration system."""

        super()._delete(uid=str(uid))
