import uuid
from typing import Optional, ClassVar, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from ..base import HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, DataSource, DataArchive


class OrchestrationSystemFields(BaseModel):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")


class OrchestrationSystem(HydroServerBaseModel):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")
    workspace_id: Optional[uuid.UUID] = None

    _editable_fields: ClassVar[set[str]] = {"name", "orchestration_system_type"}

    def __init__(self, client: "HydroServer", **data):
        super().__init__(client=client, service=client.orchestrationsystems, **data)

        self._workspace = None
        self._datasources = None
        self._dataarchives = None

    @classmethod
    def get_route(cls):
        return "orchestration-systems"

    @property
    def workspace(self) -> "Workspace":
        """The workspace this orchestration system belongs to."""

        if self._workspace is None and self.workspace_id:
            self._workspace = self.client.workspaces.get(uid=self.workspace_id)

        return self._workspace

    @property
    def datasources(self) -> List["DataSource"]:
        """The data sources associated with this workspace."""

        if self._datasources is None:
            self._datasources = self.client.datasources.list(
                orchestration_system=self.uid, fetch_all=True
            )

        return self._datasources

    @property
    def dataarchives(self) -> List["DataArchive"]:
        """The data archives associated with this workspace."""

        if self._dataarchives is None:
            self._dataarchives = self.client.dataarchives.list(
                orchestration_system=self.uid, fetch_all=True
            )

        return self._dataarchives
