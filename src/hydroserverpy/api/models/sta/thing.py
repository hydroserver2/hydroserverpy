import uuid
from typing import Optional, ClassVar, List, Dict, IO, TYPE_CHECKING
from pydantic import (
    Field,
    AliasPath,
    AliasChoices,
    AnyHttpUrl,
    field_validator
)
from ..base import HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Datastream


class Thing(HydroServerBaseModel):
    name: str = Field(..., max_length=200)
    description: str
    sampling_feature_type: str = Field(..., max_length=200)
    sampling_feature_code: str = Field(..., max_length=200)
    site_type: str = Field(..., max_length=200)
    data_disclaimer: Optional[str] = None
    is_private: bool
    latitude: float = Field(..., ge=-90, le=90, validation_alias=AliasPath("location", "latitude"))
    longitude: float = Field(..., ge=-180, le=180, validation_alias=AliasPath("location", "longitude"))
    elevation_m: Optional[float] = Field(
        None, ge=-99999, le=99999, alias="elevation_m", validation_alias=AliasPath("location", "elevation_m")
    )
    elevation_datum: Optional[str] = Field(
        None, max_length=255, validation_alias=AliasChoices("elevationDatum", AliasPath("location", "elevationDatum"))
    )
    state: Optional[str] = Field(None, max_length=200, validation_alias=AliasPath("location", "state"))
    county: Optional[str] = Field(None, max_length=200, validation_alias=AliasPath("location", "county"))
    country: Optional[str] = Field(None, max_length=2, validation_alias=AliasPath("location", "country"))
    tags: Dict[str, str]
    photos: Dict[str, AnyHttpUrl]
    workspace_id: uuid.UUID

    _editable_fields: ClassVar[set[str]] = {
        "name", "description", "sampling_feature_type", "sampling_feature_code", "site_type", "data_disclaimer",
        "is_private", "latitude", "longitude", "elevation_m", "elevation_datum", "state", "county", "country"
    }

    def __init__(self, client: "HydroServer", **data):
        super().__init__(client=client, service=client.things, **data)

        self._workspace = None
        self._datastreams = None

    @classmethod
    def get_route(cls):
        return "things"

    @property
    def workspace(self) -> "Workspace":
        """The workspace this thing belongs to."""

        if self._workspace is None:
            self._workspace = self.client.workspaces.get(uid=self.workspace_id)

        return self._workspace

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams collected at this thing."""

        if self._datastreams is None:
            self._datastreams = self.client.datastreams.list(thing=self.uid, fetch_all=True)

        return self._datastreams

    @field_validator("tags", mode="before")
    def transform_tags(cls, v):
        if isinstance(v, list):
            return {item["key"]: item["value"] for item in v if "key" in item and "value" in item}
        return v

    @field_validator("photos", mode="before")
    def transform_photos(cls, v):
        if isinstance(v, list):
            return {item["name"]: item["link"] for item in v if "name" in item and "link" in item}
        return v

    def add_tag(self, key: str, value: str):
        """Add a tag to this thing."""

        self.client.things.add_tag(uid=self.uid, key=key, value=value)
        self.tags[key] = value

    def update_tag(self, key: str, value: str):
        """Edit a tag of this thing."""

        self.client.things.update_tag(uid=self.uid, key=key, value=value)
        self.tags[key] = value

    def delete_tag(self, key: str):
        """Delete a tag of this thing."""

        self.client.things.delete_tag(uid=self.uid, key=key, value=self.tags[key])
        del self.tags[key]

    def add_photo(self, file: IO[bytes]):
        """Add a photo of this thing."""

        photo = self.client.things.add_photo(uid=self.uid, file=file)
        self.photos[photo["name"]] = photo["link"]

    def delete_photo(self, name: str):
        """Delete a photo of this thing."""

        self.client.things.delete_photo(uid=self.uid, name=name)
        del self.photos[name]
