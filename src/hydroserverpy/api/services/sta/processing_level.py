from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import ProcessingLevel


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ProcessingLevelService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = ProcessingLevel
        self._api_route = "api/data"
        self._endpoint_route = "processing-levels"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
    ) -> List["ProcessingLevel"]:
        """Fetch a collection of processing levels."""

        workspace_id = getattr(workspace, "uid", workspace)
        workspace_id = str(workspace_id) if workspace_id else None

        return super()._list(
            params={"workspace_id": workspace_id} if workspace_id else {},
        )

    def get(self, uid: Union[UUID, str]) -> "ProcessingLevel":
        """Get a processing level by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        code: str,
        definition: Optional[str] = None,
        explanation: Optional[str] = None,
    ) -> "ProcessingLevel":
        """Create a new processing level."""

        kwargs = {
            "code": code,
            "definition": definition,
            "explanation": explanation,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        code: str = ...,
        definition: Optional[str] = ...,
        explanation: Optional[str] = ...,
    ) -> "ProcessingLevel":
        """Update a processing level."""

        kwargs = {
            "code": code,
            "definition": definition,
            "explanation": explanation,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a processing level."""

        super()._delete(uid=str(uid))
