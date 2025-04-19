from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, DataSource, DataArchive


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
        self._datasources = None
        self._dataarchives = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this orchestration system belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    @property
    def datasources(self) -> List["DataSource"]:
        """The data sources associated with this workspace."""

        if self._datasources is None:
            self._datasources = self._connection.datasources.list(
                orchestration_system=self.uid
            )

        return self._datasources

    @property
    def dataarchives(self) -> List["DataArchive"]:
        """The data archives associated with this workspace."""

        if self._dataarchives is None:
            self._dataarchives = self._connection.dataarchives.list(
                orchestration_system=self.uid
            )

        return self._dataarchives

    def refresh(self):
        """Refresh this orchestration system from HydroServer."""

        super()._refresh()
        self._workspace = None
        self._datasources = None
        self._dataarchives = None

    def save(self):
        """Save changes to this orchestration system to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this orchestration system from HydroServer."""

        super()._delete()
