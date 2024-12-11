import json
from typing import Union, List, IO, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.endpoints.datastreams import DatastreamEndpoint
from hydroserverpy.core.schemas import Thing, Datastream, Tag, Photo, Archive

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


class ThingEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with thing entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `Thing`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'things'`.
    """

    def __init__(self, service: "HydroServer"):
        """
        Initialize the ThingEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = Thing
        self._api_route = self._service.api_route
        self._endpoint_route = "things"

    def list(
        self, owned_only: bool = False, primary_owned_only: bool = False
    ) -> List[Thing]:
        """
        Retrieve a collection of things owned by the logged-in user.

        :param owned_only: Only list things owned by the logged-in user.
        :param primary_owned_only: Only list things primary owned by the logged-in user.
        """

        return super()._get(
            params={
                "owned_only": owned_only,
                "primary_owned_only": primary_owned_only,
            }
        )

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> Thing:
        """
        Retrieve a thing owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=Thing)
    def create(self, **kwargs) -> Thing:
        """
        Create a new thing in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=Thing, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> Thing:
        """
        Update an existing thing in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing thing in HydroServer.
        """

        super()._delete(uid=uid)

    def list_datastreams(self, uid: Union[UUID, str]) -> List[Datastream]:
        """
        List all datastreams associated with a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :returns: A list of datastream instances.
        :rtype: List[Datastream]
        """

        response = getattr(self._service, "_request")(
            "get",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/datastreams",
        )

        endpoint = DatastreamEndpoint(self._service)

        return [
            Datastream(_endpoint=endpoint, _uid=UUID(str(entity.pop("id"))), **entity)
            for entity in json.loads(response.content)
        ]

    def list_tags(self, uid: Union[UUID, str]) -> List[Tag]:
        """
        List all tags associated with a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :returns: A list of tag instances.
        :rtype: List[Tag]
        """

        response = getattr(self._service, "_request")(
            "get", f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags"
        )

        return [
            Tag(_uid=UUID(str(entity.pop("id"))), **entity)
            for entity in json.loads(response.content)
        ]

    def create_tag(self, uid: Union[UUID, str], key: str, value: str) -> Tag:
        """
        Create a new tag for a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :param key: The key of the tag.
        :type key: str
        :param value: The value of the tag.
        :type value: str
        :returns: The created tag instance.
        :rtype: Tag
        """

        response = getattr(self._service, "_request")(
            "post",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags",
            headers={"Content-type": "application/json"},
            data=Tag(key=key, value=value).json(exclude_unset=True, by_alias=True),
        )
        entity = json.loads(response.content)

        return Tag(_uid=UUID(str(entity.pop("id"))), **entity)

    def update_tag(
        self, uid: Union[UUID, str], tag_uid: Union[UUID, str], value: str
    ) -> Tag:
        """
        Update an existing tag for a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :param tag_uid: The unique identifier of the tag.
        :type tag_uid: UUID or str
        :param value: The new value for the tag.
        :type value: str
        :returns: The updated tag instance.
        :rtype: Tag
        """

        response = getattr(self._service, "_request")(
            "patch",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags/{str(tag_uid)}",
            headers={"Content-type": "application/json"},
            data=json.dumps({"value": str(value)}),
        )
        entity = json.loads(response.content)

        return Tag(_uid=UUID(str(entity.pop("id"))), **entity)

    def delete_tag(self, uid: Union[UUID, str], tag_uid: Union[UUID, str]) -> None:
        """
        Delete a tag from a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :param tag_uid: The unique identifier of the tag.
        :type tag_uid: UUID or str
        """

        getattr(self._service, "_request")(
            "delete",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags/{str(tag_uid)}",
        )

    def list_photos(self, uid: Union[UUID, str]) -> List[Photo]:
        """
        List all photos associated with a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :returns: A list of photo instances.
        :rtype: List[Photo]
        """

        response = getattr(self._service, "_request")(
            "get", f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos"
        )

        return [
            Photo(_uid=UUID(str(entity.pop("id"))), **entity)
            for entity in json.loads(response.content)
        ]

    def upload_photo(self, uid: Union[UUID, str], file: IO) -> List[Photo]:
        """
        Upload a new photo to a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :param file: The file-like object representing the photo to upload.
        :type file: IO
        :returns: A list of photo instances created by the upload.
        :rtype: List[Photo]
        """

        response = getattr(self._service, "_request")(
            "post",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos",
            files={"files": file},
        )

        return [
            Photo(_uid=UUID(str(entity.pop("id"))), **entity)
            for entity in json.loads(response.content)
        ]

    def delete_photo(self, uid: Union[UUID, str], photo_uid: Union[UUID, str]) -> None:
        """
        Delete a photo from a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :param photo_uid: The unique identifier of the photo.
        :type photo_uid: UUID or str
        """

        getattr(self._service, "_request")(
            "delete",
            f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos/{str(photo_uid)}",
        )

    def get_archive(self, uid: Union[UUID, str]) -> Archive:
        """
        Retrieve the archive associated with a specific thing.

        :param uid: The unique identifier of the thing.
        :type uid: UUID or str
        :returns: The archive instance associated with the thing.
        :rtype: Archive
        """

        response = getattr(self._service, "_request")(
            "get", f"{self._api_route}/data/{self._endpoint_route}/{str(uid)}/archive"
        )
        entity = json.loads(response.content)

        return Archive(_uid=UUID(str(entity.pop("id"))), **entity)
