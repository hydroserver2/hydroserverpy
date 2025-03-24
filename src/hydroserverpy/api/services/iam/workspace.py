from typing import TYPE_CHECKING, Union, List
from pydantic import EmailStr
from uuid import UUID
from hydroserverpy.api.models import Workspace, Role, Collaborator
from ..base import EndpointService


if TYPE_CHECKING:
    from hydroserverpy import HydroServer


class WorkspaceService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = Workspace
        self._api_route = "api/auth"
        self._endpoint_route = "workspaces"

        super().__init__(connection)

    def list(self, associated_only: bool = False) -> List["Workspace"]:
        """Fetch a collection of HydroServer resources."""

        return super()._list(params={"associated_only": associated_only})

    def get(self, uid: Union[UUID, str]) -> "Workspace":
        """Get a workspace by ID."""

        return super()._get(uid=str(uid))

    def create(self, name: str, is_private: bool, **_) -> "Workspace":
        """Create a new workspace."""

        kwargs = {"name": name, "isPrivate": is_private}

        return super()._create(**kwargs)

    def update(
        self, uid: Union[UUID, str], name: str = ..., is_private: bool = ..., **_
    ) -> "Workspace":
        """Update a workspace."""

        kwargs = {"name": name, "isPrivate": is_private}

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a workspace."""

        super()._delete(uid=str(uid))

    def list_roles(self, uid: Union[UUID, str]) -> List["Role"]:
        """Get all roles that can be assigned within a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/roles"
        response = self._connection.request("get", path)

        return [Role(**obj) for obj in response.json()]

    def list_collaborators(self, uid: Union[UUID, str]) -> List["Collaborator"]:
        """Get all collaborators associated with a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/collaborators"
        response = self._connection.request("get", path)

        return [
            Collaborator(_connection=self._connection, workspace_id=uid, **obj)
            for obj in response.json()
        ]

    def add_collaborator(
        self, uid: Union[UUID, str], email: EmailStr, role: Union["Role", UUID, str]
    ) -> "Collaborator":
        """Add a collaborator to a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/collaborators"
        response = self._connection.request(
            "post",
            path,
            json={"email": email, "roleId": str(getattr(role, "uid", role))},
        )

        return Collaborator(
            _connection=self._connection, workspace_id=uid, **response.json()
        )

    def edit_collaborator_role(
        self, uid: Union[UUID, str], email: EmailStr, role: Union["Role", UUID, str]
    ) -> "Collaborator":
        """Edit the role of a collaborator in a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/collaborators"
        response = self._connection.request(
            "put",
            path,
            json={"email": email, "roleId": str(getattr(role, "uid", role))},
        )

        return Collaborator(
            _connection=self._connection, workspace_id=uid, **response.json()
        )

    def remove_collaborator(self, uid: Union[UUID, str], email: EmailStr) -> None:
        """Remove a collaborator from a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/collaborators"
        self._connection.request("delete", path, json={"email": email})

    def transfer_ownership(self, uid: Union[UUID, str], email: str) -> None:
        """Transfer ownership of a workspace to another HydroServer user."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/transfer"
        self._connection.request("post", path, json={"newOwner": email})

    def accept_ownership_transfer(self, uid: Union[UUID, str]) -> None:
        """Accept ownership transfer of a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/transfer"
        self._connection.request("put", path)

    def cancel_ownership_transfer(self, uid: Union[UUID, str]) -> None:
        """Cancel ownership transfer of a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/transfer"
        self._connection.request("delete", path)
