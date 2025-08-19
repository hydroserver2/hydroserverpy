from __future__ import annotations
from datetime import datetime, timedelta, timezone
from functools import cached_property
import logging
import uuid
from typing import ClassVar, TYPE_CHECKING, List, Optional, Union
import croniter
import pandas as pd
from pydantic import Field

from ..base import HydroServerBaseModel
from ..sta.datastream import Datastream
from .orchestration_system import OrchestrationSystem
from .etl_configuration import EtlConfiguration
from .schedule import Schedule
from .status import Status
from .factories import extractor_factory, transformer_factory, loader_factory
from .loaders import HydroServerLoader

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class DataSource(HydroServerBaseModel):
    name: str = Field(..., max_length=255)
    settings: EtlConfiguration
    orchestration_system_id: uuid.UUID
    schedule: Schedule
    status: Status
    workspace_id: uuid.UUID

    _editable_fields: ClassVar[set[str]] = {
        "name",
        "settings",
        "status",
        "schedule",
        "interval",
        "interval_units",
        "crontab",
        "start_time",
        "end_time",
        "last_run_successful",
        "last_run_message",
        "last_run",
        "next_run",
        "paused",
    }

    def __init__(self, client: HydroServer, **data):
        super().__init__(client=client, service=client.datasources, **data)

    @classmethod
    def get_route(cls):
        return "data-sources"

    @cached_property
    def workspace(self) -> Workspace:
        return self.client.workspaces.get(uid=self.workspace_id)

    @cached_property
    def orchestration_system(self) -> OrchestrationSystem:
        return self.client.orchestrationsystems.get(uid=self.orchestration_system_id)

    @cached_property
    def datastreams(self) -> List[Datastream]:
        return self.client.datastreams.list(data_source=self.uid, fetch_all=True).items

    # TODO: Add functions like add_payload, add_mapping, etc. and don't allow the user to manually
    # link or unlink datastreams - handle that automatically.
    def add_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Add a datastream to this data source."""

        self.client.datasources.add_datastream(uid=self.uid, datastream=datastream)

    def remove_datastream(self, datastream: Union["Datastream", uuid.UUID, str]):
        """Remove a datastream from this data source."""

        self.client.datasources.remove_datastream(uid=self.uid, datastream=datastream)

    def _next_run(self) -> Optional[str]:
        now = datetime.now(timezone.utc)
        if cron := self.schedule.crontab:
            return croniter.croniter(cron, now).get_next(datetime).isoformat()
        if iv := self.schedule.interval:
            unit = self.schedule.interval_units or "minutes"
            return (now + timedelta(**{unit: iv})).isoformat()
        return None

    def _update_status(self, loader: HydroServerLoader, success: bool, msg: str):
        short_msg = msg if len(msg) <= 255 else msg[:252] + "…"
        loader.client.datasources.update(
            uid=self.uid,
            last_run=datetime.now(timezone.utc).isoformat(),
            last_run_successful=success,
            last_run_message=short_msg,
            next_run=self._next_run(),
        )

    def is_empty(self, data):
        if data is None:
            return True
        if isinstance(data, pd.DataFrame) and data.empty:
            return True
        return False

    def load_data(self, payload_name: str = None):
        """Load data for this data source."""
        if self.status.paused is True:
            return

        if payload_name:
            self.load_data_for_payload(payload_name)
        else:
            for p in self.settings.payloads:
                self.load_data_for_payload(p.name)

    def load_data_for_payload(self, payload_name: str):
        payload = next(p for p in self.settings.payloads if p.name == payload_name)

        extractor_cls = extractor_factory(self.settings.extractor)
        transformer_cls = transformer_factory(self.settings.transformer)
        loader_cls = loader_factory(self.settings.loader, self.client, self.uid)

        try:
            logging.info("Starting extract")
            data = extractor_cls.extract(payload, loader_cls)
            if self.is_empty(data):
                self._update_status(
                    loader_cls, True, "No data returned from the extractor"
                )
                return

            logging.info("Starting transform")
            data = transformer_cls.transform(data, payload.mappings)
            if self.is_empty(data):
                self._update_status(
                    loader_cls, True, "No data returned from the transformer"
                )
                return

            logging.info("Starting load")
            loader_cls.load(data, payload)
            self._update_status(loader_cls, True, "OK")
        except Exception as e:
            self._update_status(loader_cls, False, str(e))
