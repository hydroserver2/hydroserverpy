import json
from typing import TYPE_CHECKING, Union, List, Tuple, Optional, IO, Dict, Any
from pydantic import EmailStr
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.models import Workspace, Role, Collaborator, APIKey
from hydroserverpy.api.utils import normalize_uuid
from ..base import HydroServerBaseService


if TYPE_CHECKING:
    from hydroserverpy import HydroServer


class WorkspaceService(HydroServerBaseService):
    def __init__(self, client: "HydroServer"):
        self.model = Workspace
        super().__init__(client)

    def list(
        self,
        page: int = ...,
        page_size: int = ...,
        order_by: List[str] = ...,
        is_private: bool = ...,
        is_associated: bool = ...,
        fetch_all: bool = False,
    ) -> List["Workspace"]:
        """Fetch a collection of HydroServer workspaces."""

        return super().list(
            page=page,
            page_size=page_size,
            order_by=order_by,
            fetch_all=fetch_all,
            is_private=is_private,
            is_associated=is_associated,
        )

    def create(self, name: str, is_private: bool, **_) -> "Workspace":
        """Create a new workspace."""

        return super().create(
            name=name,
            is_private=is_private,
        )

    def update(
        self, uid: Union[UUID, str], name: str = ..., is_private: bool = ..., **_
    ) -> "Workspace":
        """Update a workspace."""

        return super().update(
            uid=uid,
            name=name,
            is_private=is_private,
        )

    def list_collaborators(self, uid: Union[UUID, str]) -> List["Collaborator"]:
        """Get all collaborators associated with a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/collaborators"
        response = self.client.request("get", path)

        return [
            Collaborator(client=self.client, uid=None, workspace_id=uid, **obj)
            for obj in response.json()
        ]

    def add_collaborator(
        self, uid: Union[UUID, str], email: EmailStr, role: Union["Role", UUID, str]
    ) -> "Collaborator":
        """Add a collaborator to a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/collaborators"
        headers = {"Content-type": "application/json"}
        body = {
            "email": email,
            "roleId": normalize_uuid(role)
        }
        response = self.client.request(
            "post", path, headers=headers, data=json.dumps(body, default=self.default_serializer)
        ).json()

        return Collaborator(
            client=self.client, uid=None, workspace_id=uid, **response
        )

    def edit_collaborator_role(
        self, uid: Union[UUID, str], email: EmailStr, role: Union["Role", UUID, str], role_id: UUID
    ) -> "Collaborator":
        """Edit the role of a collaborator in a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/collaborators"
        headers = {"Content-type": "application/json"}
        body = {
            "email": email,
            "roleId": normalize_uuid(role if role is not ... else role_id)
        }

        response = self.client.request(
            "put", path, headers=headers, data=json.dumps(body, default=self.default_serializer)
        )

        return Collaborator(
            client=self.client, uid=None, workspace_id=uid, **response.json()
        )

    def remove_collaborator(self, uid: Union[UUID, str], email: EmailStr) -> None:
        """Remove a collaborator from a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/collaborators"
        self.client.request("delete", path, json={"email": email})

    def list_api_keys(self, uid: Union[UUID, str]) -> List["APIKey"]:
        """Get all API keys associated with a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys"
        response = self.client.request("get", path)

        return [
            APIKey(client=self.client, **obj)
            for obj in response.json()
        ]

    def get_api_key(self, uid: Union[UUID, str], api_key_id: Union[UUID, str]) -> "APIKey":
        """Get an API key associated with a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys/{api_key_id}"
        response = self.client.request("get", path)

        return APIKey(client=self.client, **response.json())

    def create_api_key(
        self,
        uid: Union[UUID, str],
        name: str,
        role: Union["Role", UUID, str],
        description: Optional[str] = None,
        is_active: bool = True,
        expires_at: Optional[datetime] = None
    ) -> Tuple["APIKey", str]:
        """Create an API key for a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys"
        headers = {"Content-type": "application/json"}
        body = {
            "roleId": normalize_uuid(role),
            "name": name,
            "description": description,
            "isActive": is_active,
            "expiresAt": expires_at
        }

        response = self.client.request(
            "post", path, headers=headers, data=json.dumps(body, default=self.default_serializer),
        ).json()

        return APIKey(
            client=self.client, **response
        ), response["key"]

    @staticmethod
    def _normalize_file_attachment(payload: dict) -> Dict[str, Any]:
        return {
            "id": payload.get("id"),
            "type": payload.get("type"),
            "name": payload.get("name"),
            "description": payload.get("description", ""),
            "content_type": payload.get("contentType")
            or payload.get("content_type")
            or "",
            "size_bytes": payload.get("sizeBytes") or payload.get("size_bytes") or 0,
            "link": payload.get("link"),
            "created_at": payload.get("createdAt") or payload.get("created_at"),
            "updated_at": payload.get("updatedAt") or payload.get("updated_at"),
        }

    def list_file_attachments(
        self, uid: Union[UUID, str], attachment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List file attachments associated with a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/file-attachments"
        params = {"type": attachment_type} if attachment_type else None
        response = self.client.request("get", path, params=params).json()
        if not isinstance(response, list):
            return []
        return [
            self._normalize_file_attachment(item)
            for item in response
            if isinstance(item, dict)
        ]

    def add_file_attachment(
        self,
        uid: Union[UUID, str],
        file: IO[bytes],
        attachment_type: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a file attachment to a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/file-attachments"
        data = {"type": attachment_type}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description

        response = self.client.request("post", path, data=data, files={"file": file}).json()
        return self._normalize_file_attachment(response)

    def update_file_attachment(
        self,
        uid: Union[UUID, str],
        file_attachment_id: Union[UUID, str],
        attachment_type: str = ...,
        name: str = ...,
        description: Optional[str] = ...,
    ) -> Dict[str, Any]:
        """Update workspace file attachment metadata."""

        path = (
            f"/{self.client.base_route}/{self.model.get_route()}/"
            f"{str(uid)}/file-attachments/{str(file_attachment_id)}"
        )
        body = {
            "type": attachment_type,
            "name": name,
            "description": description,
        }
        body = {k: v for k, v in body.items() if v is not ...}
        headers = {"Content-type": "application/json"}
        response = self.client.request(
            "patch",
            path,
            headers=headers,
            data=json.dumps(body, default=self.default_serializer),
        ).json()
        return self._normalize_file_attachment(response)

    def delete_file_attachment(
        self, uid: Union[UUID, str], file_attachment_id: Union[UUID, str]
    ) -> None:
        """Delete a file attachment from a workspace."""

        path = (
            f"/{self.client.base_route}/{self.model.get_route()}/"
            f"{str(uid)}/file-attachments/{str(file_attachment_id)}"
        )
        self.client.request("delete", path)

    def update_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str],
        role: Union["Role", UUID, str] = ...,
        role_id: UUID = ...,
        name: str = ...,
        description: Optional[str] = ...,
        is_active: bool = ...,
        expires_at: Optional[datetime] = ...
    ) -> "APIKey":
        """Update an existing API key."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys/{api_key_id}"
        headers = {"Content-type": "application/json"}
        body = {
            "roleId": normalize_uuid(role if role is not ... else role_id),
            "name": name,
            "description": description,
            "isActive": is_active,
            "expiresAt": expires_at
        }
        body = {k: v for k, v in body.items() if v is not ...}

        response = self.client.request(
            "patch", path, headers=headers, data=json.dumps(body, default=self.default_serializer),
        ).json()

        return APIKey(client=self.client, **response)

    def delete_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str]
    ):
        """Delete an existing API key."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys/{api_key_id}"
        self.client.request("delete", path)

    def regenerate_api_key(
        self,
        uid: Union[UUID, str],
        api_key_id: Union[UUID, str]
    ):
        """Regenerate an existing API key."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/api-keys/{api_key_id}/regenerate"
        response = self.client.request("put", path).json()

        return APIKey(
            client=self.client, **response
        ), response["key"]

    def transfer_ownership(self, uid: Union[UUID, str], email: str) -> None:
        """Transfer ownership of a workspace to another HydroServer user."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/transfer"
        self.client.request("post", path, json={"newOwner": email})

    def accept_ownership_transfer(self, uid: Union[UUID, str]) -> None:
        """Accept ownership transfer of a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/transfer"
        self.client.request("put", path)

    def cancel_ownership_transfer(self, uid: Union[UUID, str]) -> None:
        """Cancel ownership transfer of a workspace."""

        path = f"/{self.client.base_route}/{self.model.get_route()}/{str(uid)}/transfer"
        self.client.request("delete", path)
