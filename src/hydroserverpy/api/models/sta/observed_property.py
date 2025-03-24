from typing import Union, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field, AliasChoices, AliasPath
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ObservedPropertyFields(BaseModel):
    name: str = Field(..., max_length=255)
    definition: str
    description: str
    observed_property_type: str = Field(
        ...,
        max_length=255,
        serialization_alias="type",
        validation_alias=AliasChoices("type", AliasPath("properties", "variableType")),
    )
    code: str = Field(
        ...,
        max_length=255,
        validation_alias=AliasChoices("code", AliasPath("properties", "variableCode")),
    )


class ObservedProperty(HydroServerModel, ObservedPropertyFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="observedproperties", _uid=_uid, **data
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
        """The workspace this observed property belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    def refresh(self):
        """Refresh this observed property from HydroServer."""

        super()._refresh()
        self._workspace = None

    def save(self):
        """Save changes to this observed property to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this observed property from HydroServer."""

        super()._delete()
