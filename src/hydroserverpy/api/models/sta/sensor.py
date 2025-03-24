from typing import Union, Optional, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field, AliasChoices, AliasPath
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class SensorFields(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    encoding_type: str = Field(..., max_length=255)
    manufacturer: Optional[str] = Field(
        None,
        max_length=255,
        validation_alias=AliasChoices(
            "manufacturer", AliasPath("metadata", "sensorModel", "sensorManufacturer")
        ),
    )
    sensor_model: Optional[str] = Field(
        None,
        max_length=255,
        alias="model",
        validation_alias=AliasChoices(
            "model", AliasPath("metadata", "sensorModel", "sensorModelName")
        ),
    )
    sensor_model_link: Optional[str] = Field(
        None,
        max_length=500,
        alias="modelLink",
        validation_alias=AliasChoices(
            "modelLink", AliasPath("metadata", "sensorModel", "sensorModelUrl")
        ),
    )
    method_type: str = Field(
        ...,
        max_length=100,
        validation_alias=AliasChoices(
            "methodType", AliasPath("metadata", "methodType")
        ),
    )
    method_link: Optional[str] = Field(
        None,
        max_length=500,
        validation_alias=AliasChoices(
            "methodLink", AliasPath("metadata", "methodLink")
        ),
    )
    method_code: Optional[str] = Field(
        None,
        max_length=50,
        validation_alias=AliasChoices(
            "methodCode", AliasPath("metadata", "methodCode")
        ),
    )


class Sensor(HydroServerModel, SensorFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="sensors", _uid=_uid, **data
        )

        self._workspace_id = (
            data.get("workspace_id")
            or data.get("workspaceId")
            or (
                None
                if data.get("properties", {}).get("workspace") is None
                else data.get("properties", {}).get("workspace", {}).get("id")
            )
        )
        self._workspace_id = (
            str(self._workspace_id) if self._workspace_id is not None else None
        )

        self._workspace = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this sensor belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    def refresh(self):
        """Refresh this sensor from HydroServer."""

        super()._refresh()
        self._workspace = None

    def save(self):
        """Save changes to this sensor to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this sensor from HydroServer."""

        super()._delete()
