from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import Sensor, SensorCollection


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Thing, Datastream


class SensorService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Sensor
        self._collection_model = SensorCollection
        self._api_route = "api/data"
        self._endpoint_route = "sensors"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        datastream: Optional[Union["Datastream", UUID, str]] = None,
        encoding_type: Optional[str] = None,
        manufacturer: Optional[str] = None,
        method_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["Sensor"]:
        """Fetch a collection of sensors."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))
        if thing is not None:
            params["thing"] = str(getattr(thing, "uid", thing))
        if datastream is not None:
            params["datastream"] = str(getattr(datastream, "uid", datastream))
        if encoding_type is not None:
            params["encoding_type"] = encoding_type
        if manufacturer is not None:
            params["manufacturer"] = manufacturer
        if method_type is not None:
            params["method_type"] = method_type

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(self, uid: Union[UUID, str]) -> "Sensor":
        """Get a sensor by ID."""

        return super()._get(uid=str(uid))

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
