from __future__ import annotations
from functools import cached_property
import uuid
from typing import ClassVar, TYPE_CHECKING, List, Optional
from pydantic import Field
from ..base import HydroServerBaseModel
from .orchestration_system import OrchestrationSystem
from .job import Job
from .schedule import TaskSchedule
from .run import TaskRun
from .mapping import TaskMapping


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class Task(HydroServerBaseModel):
    name: str = Field(..., max_length=255)
    extractor_settings: dict = Field(default_factory=dict, alias="extractorSettings")
    transformer_settings: dict = Field(default_factory=dict, alias="transformerSettings")
    loader_settings: dict = Field(default_factory=dict, alias="loaderSettings")
    job_id: uuid.UUID
    orchestration_system_id: Optional[uuid.UUID] = None
    workspace_id: uuid.UUID
    schedule: Optional[TaskSchedule] = None
    latest_run: TaskRun
    mappings: List[TaskMapping]

    _editable_fields: ClassVar[set[str]] = {
        "name",
        "extractor_settings",
        "transformer_settings",
        "loader_settings",
        "job_id",
        "orchestration_system_id",
        "schedule",
        "mappings"
    }

    def __init__(self, client: HydroServer, **data):
        super().__init__(client=client, service=client.tasks, **data)

    @classmethod
    def get_route(cls):
        return "etl-tasks"

    @cached_property
    def workspace(self) -> Workspace:
        return self.client.workspaces.get(uid=self.workspace_id)

    @cached_property
    def orchestration_system(self) -> OrchestrationSystem:
        return self.client.orchestrationsystems.get(uid=self.orchestration_system_id)

    @cached_property
    def job(self) -> Job:
        return self.client.jobs.get(uid=self.job_id)

    def run(self):
        """"""
