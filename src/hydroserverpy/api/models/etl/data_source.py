import uuid
import tempfile
import requests
from typing import Union, ClassVar, Optional, TYPE_CHECKING, List
from pydantic import Field
from hydroserverpy.etl_csv.hydroserver_etl_csv import HydroServerETLCSV
from .orchestration_system import OrchestrationSystem
from .orchestration_configuration import OrchestrationConfigurationFields
from ..sta.datastream import Datastream
from ..base import HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class DataSource(
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
        super().__init__(client=client, service=client.datasources, **data)

        self._workspace = None
        self._orchestration_system = None
        self._datastreams = None

    @classmethod
    def get_route(cls):
        return "data-sources"

    @property
    def workspace(self) -> "Workspace":
        """The workspace this data source belongs to."""

        if self._workspace is None:
            self._workspace = self.client.workspaces.get(uid=self.workspace_id)

        return self._workspace

    @property
    def orchestration_system(self) -> "OrchestrationSystem":
        """The orchestration system that manages this data source."""

        if self._orchestration_system is None:
            self._orchestration_system = self.client.orchestrationsystems.get(uid=self.orchestration_system_id)

        return self._orchestration_system

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams this data source provides data for."""

        if self._datastreams is None:
            self._datastreams = self.client.datastreams.list(data_source=self.uid, fetch_all=True).items

        return self._datastreams

    def add_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Add a datastream to this data source."""

        self.client.datasources.add_datastream(
            uid=self.uid, datastream=datastream
        )

    def remove_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Remove a datastream from this data source."""

        self.client.datasources.remove_datastream(
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
                    self.client, data_file=data_file, data_source=self
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
                    self.client, data_file=temp_file, data_source=self
                )
                loader.run()
