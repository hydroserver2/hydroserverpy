import json
from typing import Union, List, IO, TYPE_CHECKING
from uuid import UUID
from .base import HydroServerEndpoint
from ..schemas import Thing, Datastream, Tag, Photo, Archive

if TYPE_CHECKING:
    from ..service import HydroServer


class ThingEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with Thing entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `Thing`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'things'`.
    """

    def __init__(self, service: 'HydroServer'):
        """
        Initialize the ThingEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = Thing
        self._api_route = self._service.api_route
        self._endpoint_route = 'things'

    def list_datastreams(self, uid: Union[UUID, str]) -> List[Datastream]:
        """
        List all Datastreams associated with a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :returns: A list of Datastream instances.
        :rtype: List[Datastream]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/datastreams'
        )

        return [
            Datastream(_endpoint=self, _uid=entity.pop('id'), **entity)
            for entity in json.loads(response.content)
        ]

    def list_tags(self, uid: Union[UUID, str]) -> List[Tag]:
        """
        List all Tags associated with a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :returns: A list of Tag instances.
        :rtype: List[Tag]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags'
        )

        return [Tag(_uid=entity.pop('id'), **entity) for entity in json.loads(response.content)]

    def create_tag(self, uid: Union[UUID, str], key: str, value: str) -> Tag:
        """
        Create a new Tag for a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :param key: The key of the Tag.
        :type key: str
        :param value: The value of the Tag.
        :type value: str
        :returns: The created Tag instance.
        :rtype: Tag
        """

        response = getattr(self._service, '_request')(
            'post', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags',
            headers={'Content-type': 'application/json'},
            data=Tag(key=key, value=value).json(exclude_unset=True, by_alias=True),
        )
        entity = json.loads(response.content)

        return Tag(_uid=entity.pop('id'), **entity)

    def update_tag(self, uid: Union[UUID, str], tag_uid: Union[UUID, str], value: str) -> Tag:
        """
        Update an existing Tag for a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :param tag_uid: The unique identifier of the Tag.
        :type tag_uid: UUID or str
        :param value: The new value for the Tag.
        :type value: str
        :returns: The updated Tag instance.
        :rtype: Tag
        """

        response = getattr(self._service, '_request')(
            'patch', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags/{str(tag_uid)}',
            headers={'Content-type': 'application/json'},
            data=json.dumps({'value': str(value)}),
        )
        entity = json.loads(response.content)

        return Tag(_uid=entity.pop('id'), **entity)

    def delete_tag(self, uid: Union[UUID, str], tag_uid: Union[UUID, str]) -> None:
        """
        Delete a Tag from a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :param tag_uid: The unique identifier of the Tag.
        :type tag_uid: UUID or str
        """

        getattr(self._service, '_request')(
            'delete', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/tags/{str(tag_uid)}'
        )

    def list_photos(self, uid: Union[UUID, str]) -> List[Photo]:
        """
        List all Photos associated with a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :returns: A list of Photo instances.
        :rtype: List[Photo]
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos'
        )

        return [Photo(_uid=entity.pop('id'), **entity) for entity in json.loads(response.content)]

    def upload_photo(self, uid: Union[UUID, str], file: IO) -> List[Photo]:
        """
        Upload a new Photo to a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :param file: The file-like object representing the photo to upload.
        :type file: IO
        :returns: A list of Photo instances created by the upload.
        :rtype: List[Photo]
        """

        response = getattr(self._service, '_request')(
            'post', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos',
            files={'files': file}
        )

        return [Photo(_uid=entity.pop('id'), **entity) for entity in json.loads(response.content)]

    def delete_photo(self, uid: Union[UUID, str], photo_uid: Union[UUID, str]) -> None:
        """
        Delete a Photo from a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :param photo_uid: The unique identifier of the Photo.
        :type photo_uid: UUID or str
        """

        getattr(self._service, '_request')(
            'delete', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/photos/{str(photo_uid)}'
        )

    def get_archive(self, uid: Union[UUID, str]) -> Archive:
        """
        Retrieve the Archive associated with a specific Thing.

        :param uid: The unique identifier of the Thing.
        :type uid: UUID or str
        :returns: The Archive instance associated with the Thing.
        :rtype: Archive
        """

        response = getattr(self._service, '_request')(
            'get', f'{self._api_route}/data/{self._endpoint_route}/{str(uid)}/archive'
        )
        entity = json.loads(response.content)

        return Archive(**entity)
