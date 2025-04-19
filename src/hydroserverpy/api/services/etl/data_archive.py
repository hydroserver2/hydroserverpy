from datetime import datetime
from typing import Optional, Literal, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import DataArchive, Datastream


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, OrchestrationSystem


class DataArchiveService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = DataArchive
        self._api_route = "api/data"
        self._endpoint_route = "data-archives"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        orchestration_system: Optional[Union["OrchestrationSystem", UUID, str]] = None,
    ) -> List["DataArchive"]:
        """Fetch a collection of data archives."""

        params = {}

        workspace_id = getattr(workspace, "uid", workspace)
        workspace_id = str(workspace_id) if workspace_id else None

        orchestration_system_id = getattr(
            orchestration_system, "uid", orchestration_system
        )
        orchestration_system_id = (
            str(orchestration_system_id) if orchestration_system_id else None
        )

        if workspace_id:
            params["workspace_id"] = workspace_id

        if orchestration_system_id:
            params["orchestration_system_id"] = orchestration_system_id

        return super()._list(
            params=params,
        )

    def get(self, uid: Union[UUID, str]) -> "DataArchive":
        """Get a data archive by ID."""

        return super()._get(uid=str(uid))

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
    ) -> "DataArchive":
        """Create a new data archive."""

        kwargs = {
            "name": name,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
            "orchestrationSystemId": getattr(
                orchestration_system, "uid", orchestration_system
            ),
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
                [
                    str(getattr(datastream, "uid", datastream))
                    for datastream in datastreams
                ]
                if datastreams
                else []
            ),
        }

        return super()._create(**kwargs)

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
    ) -> "DataArchive":
        """Update a data archive."""

        status_kwargs = {
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
        status_kwargs = status_kwargs if status_kwargs else ...

        schedule_kwargs = {
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
        schedule_kwargs = schedule_kwargs if schedule_kwargs else ...

        kwargs = {
            k: v
            for k, v in {
                "name": name,
                "orchestrationSystemId": getattr(
                    orchestration_system, "uid", orchestration_system
                ),
                "settings": settings,
                "schedule": schedule_kwargs,
                "status": status_kwargs,
            }.items()
            if v is not ...
        }

        return super()._update(uid=str(uid), **kwargs)

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a data archive."""

        super()._delete(uid=str(uid))

    def add_datastream(
        self, uid: Union[UUID, str], datastream: Union["Datastream", UUID, str]
    ) -> None:
        """Add a datastream to this data archive."""

        datastream_id = str(getattr(datastream, "uid", datastream))

        self._connection.request(
            "post",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/datastreams/{datastream_id}",
        )

    def remove_datastream(
        self, uid: Union[UUID, str], datastream: Union["Datastream", UUID, str]
    ) -> None:
        """Remove a datastream from this data archive."""

        datastream_id = str(getattr(datastream, "uid", datastream))

        self._connection.request(
            "delete",
            f"{self._api_route}/{self._endpoint_route}/{str(uid)}/datastreams/{datastream_id}",
        )
