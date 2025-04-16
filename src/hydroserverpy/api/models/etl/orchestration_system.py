from typing import Union, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class OrchestrationSystemFields(BaseModel):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")


class OrchestrationSystem(HydroServerModel, OrchestrationSystemFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection,
            _model_ref="orchestrationsystems",
            _uid=_uid,
            **data
        )

        self._workspace_id = str(data.get("workspace_id") or data["workspaceId"])

        self._workspace = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this orchestration system belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    def refresh(self):
        """Refresh this orchestration system from HydroServer."""

        super()._refresh()
        self._workspace = None

    def save(self):
        """Save changes to this orchestration system to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this orchestration system from HydroServer."""

        super()._delete()
