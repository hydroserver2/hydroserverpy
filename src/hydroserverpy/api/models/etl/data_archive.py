import uuid
from typing import Union, ClassVar, Optional, TYPE_CHECKING, List
from pydantic import Field
from .orchestration_system import OrchestrationSystem
from .orchestration_configuration import OrchestrationConfigurationFields
from ..sta.datastream import Datastream
from ..base import HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class DataArchive(
    HydroServerBaseModel, OrchestrationConfigurationFields
):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None
    orchestration_system_id: uuid.UUID
    workspace_id: uuid.UUID

    _editable_fields: ClassVar[set[str]] = {
        "name", "settings", "interval", "interval_units", "crontab", "start_time", "end_time", "last_run_successful",
        "last_run_message", "last_run", "next_run", "paused"
    }

    def __init__(self, client: "HydroServer", **data):
        super().__init__(client=client, service=client.dataarchives, **data)

        self._workspace = None
        self._orchestration_system = None
        self._datastreams = None

    @classmethod
    def get_route(cls):
        return "data-archives"

    @property
    def workspace(self) -> "Workspace":
        """The workspace this data archive belongs to."""

        if self._workspace is None:
            self._workspace = self.client.workspaces.get(uid=self.workspace_id)

        return self._workspace

    @property
    def orchestration_system(self) -> "OrchestrationSystem":
        """The orchestration system that manages this data archive."""

        if self._orchestration_system is None:
            self._orchestration_system = self.client.orchestrationsystems.get(uid=self.orchestration_system_id)

        return self._orchestration_system

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams this data archive provides data for."""

        if self._datastreams is None:
            self._datastreams = self.client.datastreams.list(data_archive=self.uid, fetch_all=True)

        return self._datastreams

    def add_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Add a datastream to this data archive."""

        self.client.dataarchives.add_datastream(
            uid=self.uid, datastream=datastream
        )

    def remove_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Remove a datastream from this data archive."""

        self.client.dataarchives.remove_datastream(
            uid=self.uid, datastream=datastream
        )
