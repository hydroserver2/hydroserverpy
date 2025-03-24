from typing import Union, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel

if TYPE_CHECKING:
    from hydroserverpy.api.models.iam.account import Account
    from hydroserverpy.api.models.iam.role import Role


class CollaboratorFields(BaseModel):
    user: "Account"
    role: "Role"
    workspace_id: Union[UUID, str]


class Collaborator(CollaboratorFields):
    def __init__(self, _connection, **data):
        super().__init__(**data)
        self._connection = _connection

    def edit_role(self, role: Union["Role", UUID, str]):
        """Edit the role of this workspace collaborator."""

        response = self._connection.workspaces.edit_collaborator_role(
            uid=self.workspace_id, email=self.user.email, role=role
        )
        self.role = response.role

    def remove(self):
        """Remove this collaborator from the workspace."""

        self._connection.workspaces.remove_collaborator(
            uid=self.workspace_id, email=self.user.email
        )
