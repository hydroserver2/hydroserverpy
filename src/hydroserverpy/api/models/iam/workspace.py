from typing import List, Union, Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import (
        Role,
        Collaborator,
        APIKey,
        Account,
        Thing,
        ObservedProperty,
        Sensor,
        Unit,
        ProcessingLevel,
        ResultQualifier,
        Datastream,
        OrchestrationSystem,
        DataSource,
        DataArchive,
    )


class WorkspaceFields(BaseModel):
    name: str = Field(..., max_length=255)
    is_private: bool
    owner: "Account" = Field(..., json_schema_extra={"read_only": True})
    collaborator_role: Optional["Role"] = None
    pending_transfer_to: Optional["Account"] = None


class Workspace(HydroServerModel, WorkspaceFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="workspaces", _uid=_uid, **data
        )
        self._roles = None
        self._collaborators = None
        self._things = None
        self._observedproperties = None
        self._processinglevels = None
        self._resultqualifiers = None
        self._units = None
        self._sensors = None
        self._datastreams = None
        self._orchestrationsystems = None
        self._datasources = None
        self._dataarchives = None

    @property
    def roles(self) -> List["Role"]:
        """The roles that can be assigned for this workspace."""

        if self._roles is None:
            self._roles = self._connection.workspaces.list_roles(uid=self.uid)

        return self._roles

    @property
    def collaborators(self) -> List["Collaborator"]:
        """The collaborators associated with this workspace."""

        if self._collaborators is None:
            self._collaborators = self._connection.workspaces.list_collaborators(
                uid=self.uid
            )

        return self._collaborators

    @property
    def things(self) -> List["Thing"]:
        """The things associated with this workspace."""

        if self._things is None:
            self._things = self._connection.things.list(workspace=self.uid)

        return self._things

    @property
    def observedproperties(self) -> List["ObservedProperty"]:
        """The observed properties associated with this workspace."""

        if self._observedproperties is None:
            self._observedproperties = self._connection.observedproperties.list(
                workspace=self.uid
            )

        return self._observedproperties

    @property
    def processinglevels(self) -> List["ProcessingLevel"]:
        """The processing levels associated with this workspace."""

        if self._processinglevels is None:
            self._processinglevels = self._connection.processinglevels.list(
                workspace=self.uid
            )

        return self._processinglevels

    @property
    def resultqualifiers(self) -> List["ResultQualifier"]:
        """The result qualifiers associated with this workspace."""

        if self._resultqualifiers is None:
            self._resultqualifiers = self._connection.resultqualifiers.list(
                workspace=self.uid
            )

        return self._resultqualifiers

    @property
    def units(self) -> List["Unit"]:
        """The units associated with this workspace."""

        if self._units is None:
            self._units = self._connection.units.list(workspace=self.uid)

        return self._units

    @property
    def sensors(self) -> List["Sensor"]:
        """The sensors associated with this workspace."""

        if self._sensors is None:
            self._sensors = self._connection.sensors.list(workspace=self.uid)

        return self._sensors

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams associated with this workspace."""

        if self._datastreams is None:
            self._datastreams = self._connection.datastreams.list(workspace=self.uid)

        return self._datastreams

    @property
    def orchestrationsystems(self) -> List["OrchestrationSystem"]:
        """The orchestration systems associated with this workspace."""

        if self._orchestrationsystems is None:
            self._orchestrationsystems = self._connection.orchestrationsystems.list(
                workspace=self.uid
            )

        return self._orchestrationsystems

    @property
    def datasources(self) -> List["DataSource"]:
        """The data sources associated with this workspace."""

        if self._datasources is None:
            self._datasources = self._connection.datasources.list(workspace=self.uid)

        return self._datasources

    @property
    def dataarchives(self) -> List["DataArchive"]:
        """The data archives associated with this workspace."""

        if self._dataarchives is None:
            self._dataarchives = self._connection.dataarchives.list(workspace=self.uid)

        return self._dataarchives

    def refresh(self) -> None:
        """Refresh the workspace details from HydroServer."""

        self._roles = None
        self._collaborators = None
        self._things = None
        self._observedproperties = None
        self._processinglevels = None
        self._units = None
        self._sensors = None
        self._datastreams = None
        super()._refresh()

    def save(self):
        """Save changes to this workspace to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this workspace from HydroServer."""

        super()._delete()

    def list_api_keys(self) -> List["APIKey"]:
        """Get all API keys associated with this workspace."""

        return self._connection.workspaces.list_api_keys(uid=self.uid)

    def get_api_key(self, api_key: Union["APIKey", UUID, str]) -> "APIKey":
        """Get an API key associated with this workspace."""

        return self._connection.workspaces.get_api_key(
            uid=self.uid,
            api_key_id=str(getattr(api_key, "uid", api_key))
        )

    def create_api_key(
        self,
        role: Union["Role", UUID, str],
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        expires_at: Optional[datetime] = None
    ):
        """Create an API key associated with this workspace."""

        api_key, key = self._connection.workspaces.create_api_key(
            uid=self.uid,
            role=role,
            name=name,
            description=description,
            is_active=is_active,
            expires_at=expires_at
        )

        return api_key, key

    def update_api_key(
            self,
            api_key_id: Union[UUID, str],
            role: Union["Role", UUID, str] = ...,
            name: str = ...,
            description: Optional[str] = ...,
            is_active: bool = ...,
            expires_at: Optional[datetime] = ...
    ):
        """Create an API key associated with this workspace."""

        return self._connection.workspaces.update_api_key(
            uid=self.uid,
            api_key_id=api_key_id,
            role=role,
            name=name,
            description=description,
            is_active=is_active,
            expires_at=expires_at
        )

    def delete_api_key(self, api_key_id: Union[UUID, str]):
        """Delete an API key associated with this workspace."""

        return self._connection.workspaces.delete_api_key(
            uid=self.uid,
            api_key_id=api_key_id
        )

    def regenerate_api_key(self, api_key_id: Union[UUID, str]):
        """Regenerate an API key associated with this workspace."""

        api_key, key = self._connection.workspaces.regenerate_api_key(
            uid=self.uid,
            api_key_id=api_key_id
        )

        return api_key, key

    def add_collaborator(
        self, email: EmailStr, role: Union["Role", UUID, str]
    ) -> "Collaborator":
        """Add a new collaborator to the workspace."""

        response = self._connection.workspaces.add_collaborator(
            uid=self.uid, email=email, role=role
        )
        self._collaborators = None

        return response

    def edit_collaborator_role(
        self, email: EmailStr, role: Union["Role", UUID, str]
    ) -> "Collaborator":
        """Edit a collaborator's role in this workspace."""

        response = self._connection.workspaces.edit_collaborator_role(
            uid=self.uid, email=email, role=role
        )
        self._collaborators = None

        return response

    def remove_collaborator(self, email: EmailStr) -> None:
        """Remove a collaborator from the workspace."""

        self._connection.workspaces.remove_collaborator(uid=self.uid, email=email)
        self._collaborators = None

    def transfer_ownership(self, email: EmailStr) -> None:
        """Transfer ownership of this workspace to another HydroServer user."""

        self._connection.workspaces.transfer_ownership(uid=self.uid, email=email)
        self.refresh()

    def accept_ownership_transfer(self) -> None:
        """Accept ownership transfer of this workspace."""

        self._connection.workspaces.accept_ownership_transfer(uid=self.uid)
        self.refresh()

    def cancel_ownership_transfer(self) -> None:
        """Cancel ownership transfer of this workspace."""

        self._connection.workspaces.cancel_ownership_transfer(uid=self.uid)
        self.refresh()
