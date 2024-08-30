from typing import TYPE_CHECKING
from .base import HydroServerEndpoint
from ..schemas import ObservedProperty

if TYPE_CHECKING:
    from ..service import HydroServer


class ObservedPropertyEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with ObservedProperty entities in the HydroServer service.

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
        self._endpoint_route = 'observed-properties'
