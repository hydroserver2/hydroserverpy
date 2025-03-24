from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import SensorThingsService
from hydroserverpy.api.models import Sensor


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class SensorService(SensorThingsService):
    def __init__(self, connection: "HydroServer"):
        self._model = Sensor
        self._api_route = "api/data"
        self._endpoint_route = "sensors"
        self._sta_route = "api/sensorthings/v1.1/Sensors"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> List["Sensor"]:
        """Fetch a collection of sensors."""

        params = {"$top": page_size, "$skip": page_size * (page - 1)}

        if workspace:
            params["$filter"] = (
                f"properties/workspace/id eq '{str(getattr(workspace, 'uid', workspace))}'"
            )

        return super()._list(params=params)

    def get(
        self, uid: Union[UUID, str], fetch_by_datastream_uid: bool = False
    ) -> "Sensor":
        """Get a sensor by ID."""

        return self._get(
            uid=str(uid),
            path=(
                f"api/sensorthings/v1.1/Datastreams('{str(uid)}')/Sensor"
                if fetch_by_datastream_uid
                else None
            ),
        )

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        name: str,
        description: str,
        encoding_type: str,
        method_type: str,
        manufacturer: Optional[str] = None,
        sensor_model: Optional[str] = None,
        sensor_model_link: Optional[str] = None,
        method_link: Optional[str] = None,
        method_code: Optional[str] = None,
    ) -> "Sensor":
        """Create a new sensor."""

        kwargs = {
            "name": name,
            "description": description,
            "encodingType": encoding_type,
            "methodType": method_type,
            "manufacturer": manufacturer,
            "model": sensor_model,
            "modelLink": sensor_model_link,
            "methodLink": method_link,
            "methodCode": method_code,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        name: str = ...,
        description: str = ...,
        encoding_type: str = ...,
        method_type: str = ...,
        manufacturer: Optional[str] = ...,
        sensor_model: Optional[str] = ...,
        sensor_model_link: Optional[str] = ...,
        method_link: Optional[str] = ...,
        method_code: Optional[str] = ...,
    ) -> "Sensor":
        """Update a sensor."""

        kwargs = {
            "name": name,
            "description": description,
            "encodingType": encoding_type,
            "methodType": method_type,
            "manufacturer": manufacturer,
            "model": sensor_model,
            "modelLink": sensor_model_link,
            "methodLink": method_link,
            "methodCode": method_code,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a sensor."""

        super()._delete(uid=str(uid))
