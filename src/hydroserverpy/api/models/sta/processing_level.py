from typing import Union, Optional, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ProcessingLevelFields(BaseModel):
    code: str = Field(..., max_length=255)
    definition: Optional[str] = None
    explanation: Optional[str] = None


class ProcessingLevel(HydroServerModel, ProcessingLevelFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="processinglevels", _uid=_uid, **data
        )

        self._workspace_id = str(data.get("workspace_id") or data["workspaceId"])

        self._workspace = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this processing level belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    def refresh(self):
        """Refresh this processing level from HydroServer."""

        super()._refresh()
        self._workspace = None

    def save(self):
        """Save changes to this processing level to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this processing level from HydroServer."""

        super()._delete()
