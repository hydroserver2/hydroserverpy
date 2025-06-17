from typing import TYPE_CHECKING, Union, List, Tuple, Optional
from pydantic import EmailStr
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.models import Workspace, Role, Collaborator, APIKey
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

    def list_api_keys(self, uid: Union[UUID, str]) -> List["APIKey"]:
        """Get all API keys associated with a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys"
        response = self._connection.request("get", path)

        return [APIKey(_connection=self._connection, _uid=UUID(str(obj.pop("id"))), **obj) for obj in response.json()]

    def get_api_key(self, uid: Union[UUID, str], api_key_id: Union[UUID, str]) -> "APIKey":
        """Get an API key associated with a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys/{api_key_id}"
        response = self._connection.request("get", path).json()

        return APIKey(_connection=self._connection, _uid=UUID(str(response.pop("id"))), **response)

    def create_api_key(
        self,
        uid: Union[UUID, str],
        role: Union["Role", UUID, str],
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        expires_at: Optional[datetime] = None
    ) -> Tuple["APIKey", str]:
        """Create an API key for a workspace."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys"
        kwargs = {
            "roleId": str(getattr(role, "uid", role)),
            "name": name,
            "description": description,
            "isActive": is_active,
            "expiresAt": expires_at
        }
        headers = {"Content-type": "application/json"}

        response = self._connection.request(
            "post", path, headers=headers, json=self._to_iso_time(kwargs)
        ).json()

        return APIKey(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        ), response["key"]

    def update_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str],
        role: Union["Role", UUID, str] = ...,
        name: str = ...,
        description: Optional[str] = ...,
        is_active: bool = ...,
        expires_at: Optional[datetime] = ...
    ) -> "APIKey":
        """Update an existing API key."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys/{str(api_key_id)}"
        kwargs = {
            "roleId": ... if role is ... else str(getattr(role, "uid", role)),
            "name": name,
            "description": description,
            "isActive": is_active,
            "expiresAt": (
                expires_at.isoformat()
                if expires_at
                not in (
                    None,
                    ...,
                )
                else expires_at
            )
        }
        headers = {"Content-type": "application/json"}

        response = self._connection.request(
            "patch", path, headers=headers,
            json={k: v for k, v in kwargs.items() if v is not ...}
        ).json()

        return APIKey(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        )

    def delete_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str]
    ):
        """Delete an existing API key."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys/{str(api_key_id)}"
        self._connection.request("delete", path)

    def regenerate_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str]
    ):
        """Regenerate an existing API key."""

        path = f"/{self._api_route}/{self._endpoint_route}/{str(uid)}/api-keys/{str(api_key_id)}/regenerate"
        response = self._connection.request("put", path).json()

        return APIKey(
            _connection=self._connection, _uid=UUID(str(response.pop("id"))), **response
        ), response["key"]

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
