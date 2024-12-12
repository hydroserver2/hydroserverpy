from typing import Union, List, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.schemas import ObservedProperty

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


class ObservedPropertyEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with observed property entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `ObservedProperty`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'observed-properties'`.
    """

    def __init__(self, service):
        """
        Initialize the ObservedPropertyEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = ObservedProperty
        self._api_route = self._service.api_route
        self._endpoint_route = "observed-properties"

    def list(
        self,
        include_owned: bool = True,
        include_unowned: bool = True,
        include_templates: bool = True,
    ) -> List[ObservedProperty]:
        """
        Retrieve a collection of observed properties.

        :param include_owned: Whether to include owned observed properties.
        :param include_unowned: Whether to include unowned observed properties.
        :param include_templates: Whether to include template observed properties.
        """

        if (
            include_owned is True
            and include_unowned is True
            and include_templates is True
        ):
            owner = "anyUserOrNoUser"
        elif (
            include_owned is True
            and include_unowned is True
            and include_templates is False
        ):
            owner = "anyUser"
        elif (
            include_owned is True
            and include_unowned is False
            and include_templates is True
        ):
            owner = "currentUserOrNoUser"
        elif (
            include_owned is True
            and include_unowned is False
            and include_templates is False
        ):
            owner = "currentUser"
        elif (
            include_owned is False
            and include_unowned is False
            and include_templates is True
        ):
            owner = "noUser"
        else:
            return []

        return super()._get(params={"owner": owner})

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> ObservedProperty:
        """
        Retrieve an observed property owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=ObservedProperty)
    def create(self, **kwargs) -> ObservedProperty:
        """
        Create a new observed property in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=ObservedProperty, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> ObservedProperty:
        """
        Update an existing observed property in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing observed property in HydroServer.
        """

        super()._delete(uid=uid)
