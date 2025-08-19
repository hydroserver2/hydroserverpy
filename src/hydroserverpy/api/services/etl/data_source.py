from typing import Optional, Union, List, Literal, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.models import DataSource
from hydroserverpy.api.utils import normalize_uuid
from ..base import HydroServerBaseService

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, OrchestrationSystem, Datastream


class DataSourceService(HydroServerBaseService):
    def __init__(self, client: "HydroServer"):
        self.model = DataSource
        super().__init__(client)

    def list(
        self,
        page: int = ...,
        page_size: int = ...,
        order_by: List[str] = ...,
        workspace: Optional[Union["Workspace", UUID, str]] = ...,
        datastream: Optional[Union["Datastream", UUID, str]] = ...,
        orchestration_system: Optional[Union["OrchestrationSystem", UUID, str]] = ...,
        fetch_all: bool = False,
    ) -> List["DataSource"]:
        """Fetch a collection of data sources."""

        return super().list(
            page=page,
            page_size=page_size,
            order_by=order_by,
            workspace_id=normalize_uuid(workspace),
            datastream_id=normalize_uuid(datastream),
            orchestration_system_id=normalize_uuid(orchestration_system),
            fetch_all=fetch_all,
        )

    def create(
        self,
        name: str,
        workspace: Union["Workspace", UUID, str],
        orchestration_system: Union["OrchestrationSystem", UUID, str],
        settings: Optional[dict] = None,
        interval: Optional[int] = None,
        interval_units: Optional[Literal["minutes", "hours", "days"]] = None,
        crontab: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        last_run_successful: Optional[bool] = None,
        last_run_message: Optional[str] = None,
        last_run: Optional[datetime] = None,
        next_run: Optional[datetime] = None,
        paused: bool = False,
        datastreams: Optional[List[Union["Datastream", UUID, str]]] = None,
    ) -> "DataSource":
        """Create a new data source."""

        body = {
            "name": name,
            "workspaceId": normalize_uuid(workspace),
            "orchestrationSystemId": normalize_uuid(orchestration_system),
            "settings": settings,
            "schedule": {
                "interval": interval,
                "intervalUnits": interval_units,
                "crontab": crontab,
                "startTime": start_time,
                "endTime": end_time,
            },
            "status": {
                "lastRunSuccessful": last_run_successful,
                "lastRunMessage": last_run_message,
                "lastRun": last_run,
                "nextRun": next_run,
                "paused": paused,
            },
            "datastreamIds": (
                [normalize_uuid(datastream) for datastream in datastreams]
                if datastreams
                else []
            ),
        }

        return super().create(**body)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        orchestration_system: Union["OrchestrationSystem", UUID, str] = ...,
        settings: Optional[dict] = ...,
        interval: Optional[int] = ...,
        interval_units: Optional[Literal["minutes", "hours", "days"]] = ...,
        crontab: Optional[str] = ...,
        start_time: Optional[datetime] = ...,
        end_time: Optional[datetime] = ...,
        last_run_successful: Optional[bool] = ...,
        last_run_message: Optional[str] = ...,
        last_run: Optional[datetime] = ...,
        next_run: Optional[datetime] = ...,
        paused: bool = ...,
    ) -> "DataSource":
        """Update a data source."""

        status_body = {
            k: v
            for k, v in {
                "lastRunSuccessful": last_run_successful,
                "lastRunMessage": last_run_message,
                "lastRun": last_run,
                "nextRun": next_run,
                "paused": paused,
            }.items()
            if v is not ...
        }
        status_body = status_body if status_body else ...

        schedule_body = {
            k: v
            for k, v in {
                "interval": interval,
                "intervalUnits": interval_units,
                "crontab": crontab,
                "startTime": start_time,
                "endTime": end_time,
            }.items()
            if v is not ...
        }
        schedule_body = schedule_body if schedule_body else ...

        body = {
            k: v
            for k, v in {
                "name": name,
                "orchestrationSystemId": getattr(
                    orchestration_system, "uid", orchestration_system
                ),
                "settings": settings,
                "schedule": schedule_body,
                "status": status_body,
            }.items()
            if v is not ...
        }

        return super().update(uid=str(uid), **body)

    def add_datastream(
        self, uid: Union[UUID, str], datastream: Union["Datastream", UUID, str]
    ) -> None:
        """Add a datastream to this data source."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/datastreams/{normalize_uuid(datastream)}"
        self.client.request("put", path)

    def remove_datastream(
        self, uid: Union[UUID, str], datastream: Union["Datastream", UUID, str]
    ) -> None:
        """Remove a datastream from this data source."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/datastreams/{normalize_uuid(datastream)}"
        self.client.request("delete", path)
