from typing import List, Union, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.schemas import ProcessingLevel

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


class ProcessingLevelEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with processing level entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `ProcessingLevel`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'processing-levels'`.
    """

    def __init__(self, service):
        """
        Initialize the ProcessingLevelEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = ProcessingLevel
        self._api_route = self._service.api_route
        self._endpoint_route = 'processing-levels'

    def list(self) -> List[ProcessingLevel]:
        """
        Retrieve a collection of processing levels owned by the logged-in user.
        """

        return super()._get()

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> ProcessingLevel:
        """
        Retrieve a processing level owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=ProcessingLevel)
    def create(self, **kwargs) -> ProcessingLevel:
        """
        Create a new processing level in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=ProcessingLevel, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> ProcessingLevel:
        """
        Update an existing processing level in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing processing level in HydroServer.
        """

        super()._delete(uid=uid)
