import requests
import tempfile
from typing import Union, List, Optional, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field
from hydroserverpy.etl_csv.hydroserver_etl_csv import HydroServerETLCSV
from .orchestration_system import OrchestrationSystem
from .orchestration_configuration import OrchestrationConfigurationFields
from ..sta.datastream import Datastream
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class DataSourceFields(BaseModel):
    name: str = Field(..., max_length=255)
    settings: Optional[dict] = None


class DataSource(HydroServerModel, DataSourceFields, OrchestrationConfigurationFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="datasources", _uid=_uid, **data
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
        """The workspace this data source belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    @property
    def orchestration_system(self) -> "OrchestrationSystem":
        """The orchestration system that manages this data source."""

        if self._orchestration_system is None and self._orchestration_system_id:
            self._orchestration_system = self._connection.orchestration_systems.get(
                uid=self._orchestration_system_id
            )

        return self._orchestration_system

    @orchestration_system.setter
    def orchestration_system(
        self, orchestration_system: Union["OrchestrationSystem", UUID, str]
    ):
        if not orchestration_system:
            raise ValueError("Orchestration system of data source cannot be None.")
        if str(getattr(orchestration_system, "uid", orchestration_system)) != str(
            self.orchestration_system.uid
        ):
            self._orchestration_system = self._connection.orchestrationsystems.get(
                uid=str(getattr(orchestration_system, "uid", orchestration_system))
            )

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams this data source provides data for."""

        if self._datastreams is None:
            data_source = self._connection.datasources.get(uid=self.uid)
            self._datastreams = data_source.datastreams

        return self._datastreams

    def refresh(self):
        """Refresh this data source from HydroServer."""

        super()._refresh()
        self._workspace = None
        self._datastreams = None

    def save(self):
        """Save changes to this data source to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this data source from HydroServer."""

        super()._delete()

    def add_datastream(self, datastream: Union["Datastream", UUID, str]):
        """Add a datastream to this data source."""

        self._connection.datasources.add_datastream(uid=self.uid, datastream=datastream)

    def remove_datastream(self, datastream: Union["Datastream", UUID, str]):
        """Remove a datastream from this data source."""

        self._connection.datasources.remove_datastream(
            uid=self.uid, datastream=datastream
        )

    # TODO: Replace with ETL module.
    def load_data(self):
        """Load data for this data source."""

        if self.paused is True:
            return

        if self.settings["extractor"]["type"] == "local":
            with open(self.settings["extractor"]["sourceUri"]) as data_file:
                loader = HydroServerETLCSV(
                    self._connection, data_file=data_file, data_source=self
                )
                loader.run()
        elif self.settings["extractor"]["type"] == "HTTP":
            with tempfile.NamedTemporaryFile(mode="w+") as temp_file:
                response = requests.get(
                    self.settings["extractor"]["sourceUri"],
                    stream=True,
                    timeout=60,
                )
                response.raise_for_status()
                chunk_size = 1024 * 1024 * 10  # Use a 10mb chunk size.
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        temp_file.write(chunk.decode("utf-8"))
                temp_file.seek(0)
                loader = HydroServerETLCSV(
                    self._connection, data_file=temp_file, data_source=self
                )
                loader.run()
