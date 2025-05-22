from typing import Optional, Union, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Role


class APIKeyFields(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    role: "Role"


class APIKey(HydroServerModel, APIKeyFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="apikeys", _uid=_uid, **data
        )

        self._workspace_id = str(data.get("workspace_id") or data["workspaceId"])
        self._workspace = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this data source belongs to."""

        if self._workspace is None and self._workspace_id:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    def refresh(self):
        """Refresh this data source from HydroServer."""

        self._original_data = (
            self._connection.workspaces.get_api_key(
                uid=self._workspace_id, api_key_id=self.uid
            ).model_dump(exclude=["uid"])
        )
        self.__dict__.update(self._original_data)
        self._workspace = None

    def save(self):
        """Save changes to this data source to HydroServer."""

        if self._patch_data:
            api_key = self._connection.workspaces.update_api_key(
                uid=self._workspace_id, api_key_id=self.uid, **self._patch_data
            )
            self._original_data = api_key.dict(by_alias=False, exclude=["uid"])
            self.__dict__.update(self._original_data)

    def delete(self):
        """Delete this data source from HydroServer."""

        if not self._uid:
            raise AttributeError("This resource cannot be deleted: UID is not set.")

        self._connection.workspaces.delete_api_key(
            uid=self._workspace_id, api_key_id=self.uid
        )
        self._uid = None

    def regenerate(self):
        """Regenerates this API key. WARNING: Previous key will be invalidated."""

        _, key = self._connection.workspaces.regenerate_api_key(
            uid=self._workspace_id, api_key_id=self.uid
        )

        return key
