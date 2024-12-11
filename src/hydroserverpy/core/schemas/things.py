from pydantic import BaseModel, Field, AliasPath, AliasChoices, field_validator
from typing import Optional, List, Literal, IO, TYPE_CHECKING
from uuid import UUID
from country_list import countries_for_language
from hydroserverpy.core.schemas.base import HydroServerCoreModel, HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy.core.schemas.datastreams import Datastream


class ThingFields(BaseModel):
    name: str = Field(
        ...,
        strip_whitespace=True,
        max_length=200,
        description="The name of the site/thing.",
    )
    description: str = Field(
        ..., strip_whitespace=True, description="A description of the site/thing."
    )
    sampling_feature_type: str = Field(
        ...,
        strip_whitespace=True,
        max_length=200,
        description="The sampling feature type of the site/thing.",
    )
    sampling_feature_code: str = Field(
        ...,
        strip_whitespace=True,
        max_length=200,
        description="A code representing the sampling feature of the site/thing.",
    )
    site_type: str = Field(
        ...,
        strip_whitespace=True,
        max_length=200,
        description="The type of the site/thing.",
    )
    data_disclaimer: Optional[str] = Field(
        None,
        strip_whitespace=True,
        description="An optional data disclaimer to attach to observations collected at this site/thing.",
    )


# Get a list of all ISO 3166-1 alpha-2 country codes
valid_country_codes = [code for code, _ in countries_for_language("en")]


class LocationFields(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        serialization_alias="latitude",
        validation_alias=AliasChoices("latitude", AliasPath("location", "latitude")),
        description="The WGS84 latitude of the location.",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        serialization_alias="longitude",
        validation_alias=AliasChoices("longitude", AliasPath("location", "longitude")),
        description="The WGS84 longitude of the location.",
    )
    elevation_m: Optional[float] = Field(
        None,
        ge=-99999,
        le=99999,
        serialization_alias="elevation_m",
        validation_alias=AliasChoices(
            "elevation_m", AliasPath("location", "elevation_m")
        ),
        description="The elevation in meters of the location.",
    )
    elevation_datum: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=255,
        serialization_alias="elevationDatum",
        validation_alias=AliasChoices(
            "elevationDatum", AliasPath("location", "elevationDatum")
        ),
        description="The datum used to represent the elevation of the location.",
    )
    state: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=200,
        serialization_alias="state",
        validation_alias=AliasChoices("state", AliasPath("location", "state")),
        description="The state/province of the location.",
    )
    county: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=200,
        serialization_alias="county",
        validation_alias=AliasChoices("county", AliasPath("location", "county")),
        description="The county/district of the location.",
    )
    country: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=2,
        serialization_alias="country",
        validation_alias=AliasChoices("country", AliasPath("location", "country")),
        description="The ISO 3166-1 alpha-2 country code of the location.",
    )

    @field_validator("country", mode="after")
    def check_country_code(cls, value: str) -> str:
        """
        Validate the country code to ensure it is an ISO 3166-1 alpha-2 country code.

        :param value: The country code to validate.
        :type value: Optional[str]
        :raises ValueError: If the country code is invalid.
        :return: The validated country code.
        :rtype: Optional[str]
        """

        if value and value.upper() not in valid_country_codes:
            raise ValueError(
                f"Invalid country code: {value}. Must be an ISO 3166-1 alpha-2 country code."
            )

        return value


class Thing(HydroServerCoreModel, ThingFields, LocationFields):
    """
    A model representing a site/thing, combining core attributes from ThingFields and LocationFields with methods for
    interacting with related entities.

    :ivar _datastreams: A private attribute to cache the list of datastreams associated with the thing.
    :ivar _tags: A private attribute to cache the list of tags associated with the thing.
    :ivar _photos: A private attribute to cache the list of photos associated with the thing.
    :ivar _archive: A private attribute to cache the archive associated with the thing.
    """

    def __init__(self, _endpoint, _uid: Optional[UUID] = None, **data):
        """
        Initialize a Thing instance.

        :param _endpoint: The endpoint associated with the thing.
        :type _endpoint: str
        :param _uid: The unique identifier for the thing.
        :type _uid: Optional[UUID]
        :param data: Additional attributes for the thing.
        """

        super().__init__(_endpoint=_endpoint, _uid=_uid, **data)
        self._datastreams = None
        self._tags = None
        self._photos = None
        self._archive = None

    @property
    def datastreams(self) -> List["Datastream"]:
        """
        The datastreams associated with the thing. If not already cached, fetch the datastreams from the
        server.

        :return: A list of datastreams associated with the thing.
        :rtype: List[Datastream]
        """

        if self._datastreams is None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)

        return self._datastreams

    @property
    def tags(self) -> List["Tag"]:
        """
        The tags associated with the thing. If not already cached, fetch the tags from the server.

        :return: A list of tags associated with the thing.
        :rtype: List[Tag]
        """

        if self._tags is None:
            self._tags = self._endpoint.list_tags(uid=self.uid)

        return self._tags

    @property
    def photos(self) -> List["Photo"]:
        """
        The photos associated with the thing. If not already cached, fetch the photos from the server.

        :return: A list of photos associated with the thing.
        :rtype: List[Photo]
        """

        if self._photos is None:
            self._photos = self._endpoint.list_photos(uid=self.uid)

        return self._photos

    @property
    def archive(self) -> "Archive":
        """
        The archive associated with the thing. If not already cached, fetch the archive from the server.

        :return: The archive associated with the thing.
        :rtype: Archive
        """

        if self._archive is None:
            self._archive = self._endpoint.get_archive(uid=self.uid)

        return self._archive

    def refresh(self) -> None:
        """
        Refresh the thing with the latest data from the server and update cached datastreams, tags, photos, and archive
        if they were previously loaded.
        """

        entity = self._endpoint.get(uid=self.uid).model_dump(exclude=["uid"])
        self._original_data = entity
        self.__dict__.update(entity)
        if self._datastreams is not None:
            self._datastreams = self._endpoint.list_datastreams(uid=self.uid)
        if self._tags is not None:
            self._tags = self._endpoint.list_tags(uid=self.uid)
        if self._photos is not None:
            self._photos = self._endpoint.list_photos(uid=self.uid)
        if self._archive is not None:
            self._archive = self._endpoint.get_archive(uid=self.uid)

    def add_tag(self, key: str, value: str) -> None:
        """
        Add a new tag to the thing.

        :param key: The key of the new tag.
        :param value: The value of the new tag.
        """

        if self.tags is not None:
            new_tag = self._endpoint.create_tag(uid=self.uid, key=key, value=value)
            self._tags.append(new_tag)

    def update_tag(self, key: str, value: str) -> None:
        """
        Update the value of an existing tag on the thing.

        :param key: The key of the tag to update.
        :param value: The new value for the tag.
        """

        selected_tag = next((tag for tag in self._tags if tag.key == key))
        updated_tag = self._endpoint.update_tag(
            uid=self.uid, tag_uid=selected_tag.uid, value=value
        )
        self._tags = [tag if tag.key != key else updated_tag for tag in self._tags]

    def delete_tag(self, key: str) -> None:
        """
        Delete a tag from the thing.

        :param key: The key of the tag to delete.
        """

        selected_tag = next((tag for tag in self._tags if tag.key == key))
        self._endpoint.delete_tag(uid=self.uid, tag_uid=selected_tag.uid)
        self._tags = [tag for tag in self._tags if tag.key != selected_tag.key]

    def add_photo(self, photo: IO) -> None:
        """
        Add a photo to the thing.

        :param photo: The photo file to upload.
        :type photo: IO
        """

        if self.photos is not None:
            photos = self._endpoint.upload_photo(uid=self.uid, file=photo)
            self._photos.extend(photos)

    def delete_photo(self, link: str) -> None:
        """
        Delete a photo from the thing.

        :param link: The link to the photo to delete.
        """

        selected_photo = next((photo for photo in self._photos if photo.link == link))
        self._endpoint.delete_photo(uid=self.uid, photo_uid=selected_photo.uid)
        self._photos = [
            photo for photo in self._photos if photo.link != selected_photo.link
        ]


class Archive(HydroServerBaseModel):
    """
    A model representing an archive associated with a thing.
    """

    link: Optional[str] = Field(
        None,
        strip_whitespace=True,
        max_length=255,
        description="A link to the HydroShare resource containing the archived site/thing.",
    )
    frequency: Optional[Literal["daily", "weekly", "monthly"]] = Field(
        ...,
        description="The frequency at which the site/thing should be archived.",
    )
    path: str = Field(
        ...,
        strip_whitespace=True,
        max_length=255,
        description="The path within the HydroShare resource containing the archived data.",
    )
    datastream_ids: List[UUID] = Field(
        ...,
        description="The list of datastreams that are included in the archived data.",
    )


class Tag(HydroServerBaseModel):
    """
    A model representing a tag associated with a thing.
    """

    key: str = Field(
        ..., strip_whitespace=True, max_length=255, description="The key of the tag."
    )
    value: str = Field(
        ..., strip_whitespace=True, max_length=255, description="The value of the tag."
    )


class Photo(HydroServerBaseModel):
    """
    A model representing a photo associated with a thing.
    """

    file_path: str = Field(
        ..., strip_whitespace=True, description="The file path of the photo."
    )
    link: str = Field(..., strip_whitespace=True, description="The link to the photo.")
