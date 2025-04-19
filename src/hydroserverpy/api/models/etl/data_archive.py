from typing import Union, Optional, TYPE_CHECKING, List
from uuid import UUID
from pydantic import BaseModel, Field
from .orchestration_system import OrchestrationSystem
from .orchestration_configuration import OrchestrationConfigurationFields
from ..sta.datastream import Datastream
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class DataArchiveFields(BaseModel):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataArchive(
    HydroServerModel, DataArchiveFields, OrchestrationConfigurationFields
):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="dataarchives", _uid=_uid, **data
        )

        self._workspace_id = str(data.get("workspace_id") or data["workspaceId"])
        self._orchestration_system_id = str(
            data.get("orchestration_system_id") or data["orchestrationSystem"]["id"]
        )

        self._workspace = None

        if data.get("orchestrationSystem"):
            self._orchestration_system = OrchestrationSystem(
                _connection=_connection,
                _uid=self._orchestration_system_id,
                **data["orchestrationSystem"]
            )
        else:
            self._orchestration_system = None

        if data.get("datastreams"):
            self._datastreams = [
                Datastream(_connection=_connection, _uid=datastream["id"], **datastream)
                for datastream in data["datastreams"]
            ]
        else:
            self._datastreams = []

    @property
    def workspace(self) -> "Workspace":
        """The workspace this data archive belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    @property
    def orchestration_system(self) -> "OrchestrationSystem":
        """The orchestration system that manages this data archive."""

        if self._orchestration_system is None and self._orchestration_system_id:
            self._orchestration_system = self._connection.orchestration_systems.get(
                uid=self._orchestration_system_id
            )

        return self._orchestration_system

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams this data archive provides data for."""

        return self._datastreams

    def refresh(self):
        """Refresh this data archive from HydroServer."""

        super()._refresh()
        self._workspace = None

    def save(self):
        """Save changes to this data archive to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this data archive from HydroServer."""

        super()._delete()

    def add_datastream(self, datastream: Union["Datastream", UUID, str]):
        """Add a datastream to this data archive."""

        self._connection.dataarchives.add_datastream(
            uid=self.uid, datastream=datastream
        )

    def remove_datastream(self, datastream: Union["Datastream", UUID, str]):
        """Remove a datastream from this data archive."""

        self._connection.dataarchives.remove_datastream(
            uid=self.uid, datastream=datastream
        )
