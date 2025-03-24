from typing import Optional, Union, List, Dict, IO, TYPE_CHECKING
from uuid import UUID
from pydantic import (
    BaseModel,
    Field,
    AliasChoices,
    AliasPath,
    AnyHttpUrl,
    field_validator,
)
from ..base import HydroServerModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Datastream


class ThingFields(BaseModel):
    name: str = Field(..., max_length=200)
    description: str
    sampling_feature_type: str = Field(
        ...,
        max_length=200,
        validation_alias=AliasChoices(
            "samplingFeatureType", AliasPath("properties", "samplingFeatureType")
        ),
    )
    sampling_feature_code: str = Field(
        ...,
        max_length=200,
        validation_alias=AliasChoices(
            "samplingFeatureCode", AliasPath("properties", "samplingFeatureCode")
        ),
    )
    site_type: str = Field(
        ...,
        max_length=200,
        validation_alias=AliasChoices("siteType", AliasPath("properties", "siteType")),
    )
    tags: Dict[str, str] = Field(
        ...,
        json_schema_extra={"editable": False, "read_only": True},
        validation_alias=AliasChoices("tags", AliasPath("properties", "tags")),
    )
    photos: Dict[str, AnyHttpUrl] = Field(
        ...,
        json_schema_extra={"editable": False, "read_only": True},
        validation_alias=AliasChoices("photos", AliasPath("properties", "photos")),
    )
    data_disclaimer: Optional[str] = Field(
        None,
        validation_alias=AliasChoices(
            "dataDisclaimer", AliasPath("properties", "dataDisclaimer")
        ),
    )
    is_private: bool = Field(
        ...,
        validation_alias=AliasChoices(
            "isPrivate", AliasPath("properties", "isPrivate")
        ),
    )

    @field_validator("tags", mode="before")
    def convert_tags(
        cls, value: Union[List[Dict[str, str]], Dict[str, str]]
    ) -> Dict[str, str]:
        if isinstance(value, list):
            return {item["key"]: item["value"] for item in value}
        return value

    @field_validator("photos", mode="before")
    def convert_photos(
        cls, value: Union[List[Dict[str, str]], Dict[str, str]]
    ) -> Dict[str, str]:
        if isinstance(value, list):
            return {item["name"]: item["link"] for item in value}
        return value


class LocationFields(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        validation_alias=AliasChoices(
            "latitude",
            AliasPath("Locations", 0, "location", "geometry", "coordinates", 0),
        ),
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        validation_alias=AliasChoices(
            "longitude",
            AliasPath("Locations", 0, "location", "geometry", "coordinates", 1),
        ),
    )
    elevation_m: Optional[float] = Field(
        None,
        ge=-99999,
        le=99999,
        validation_alias=AliasChoices(
            "elevation_m", AliasPath("Locations", 0, "properties", "elevation_m")
        ),
    )
    elevation_datum: Optional[str] = Field(
        None,
        max_length=255,
        validation_alias=AliasChoices(
            "elevationDatum", AliasPath("Locations", 0, "properties", "elevationDatum")
        ),
    )
    state: Optional[str] = Field(
        None,
        max_length=200,
        validation_alias=AliasChoices(
            "state", AliasPath("Locations", 0, "properties", "state")
        ),
    )
    county: Optional[str] = Field(
        None,
        max_length=200,
        validation_alias=AliasChoices(
            "county", AliasPath("Locations", 0, "properties", "county")
        ),
    )
    country: Optional[str] = Field(
        None,
        max_length=2,
        validation_alias=AliasChoices(
            "country", AliasPath("Locations", 0, "properties", "country")
        ),
    )


class Thing(HydroServerModel, ThingFields, LocationFields):
    def __init__(self, _connection: "HydroServer", _uid: Union[UUID, str], **data):
        super().__init__(
            _connection=_connection, _model_ref="things", _uid=_uid, **data
        )

        self._workspace_id = str(
            data.get("workspace_id")
            or data.get("workspaceId")
            or data["properties"]["workspace"]["id"]
        )

        self._workspace = None
        self._datastreams = None
        self._photos = None
        self._tags = None

    @property
    def workspace(self) -> "Workspace":
        """The workspace this thing belongs to."""

        if self._workspace is None:
            self._workspace = self._connection.workspaces.get(uid=self._workspace_id)

        return self._workspace

    @property
    def datastreams(self) -> List["Datastream"]:
        """The datastreams collected at this thing."""

        if self._datastreams is None:
            self._datastreams = self._connection.datastreams.list(thing=self.uid)

        return self._datastreams

    def refresh(self):
        """Refresh this thing from HydroServer."""

        super()._refresh()
        self._workspace = None
        self._datastreams = None

    def save(self):
        """Save changes to this thing to HydroServer."""

        super()._save()

    def delete(self):
        """Delete this thing from HydroServer."""

        super()._delete()

    def add_tag(self, key: str, value: str):
        """Add a tag to this thing."""

        self._connection.things.add_tag(uid=self.uid, key=key, value=value)
        self.tags[key] = value

    def update_tag(self, key: str, value: str):
        """Edit a tag of this thing."""

        self._connection.things.update_tag(uid=self.uid, key=key, value=value)
        self.tags[key] = value

    def delete_tag(self, key: str):
        """Delete a tag of this thing."""

        self._connection.things.delete_tag(uid=self.uid, key=key)
        del self.tags[key]

    def add_photo(self, file: IO[bytes]):
        """Add a photo of this thing."""

        photo = self._connection.things.add_photo(uid=self.uid, file=file)
        self.photos[photo["name"]] = photo["link"]

    def delete_photo(self, name: str):
        """Delete a photo of this thing."""

        self._connection.things.delete_photo(uid=self.uid, name=name)
        del self.photos[name]
