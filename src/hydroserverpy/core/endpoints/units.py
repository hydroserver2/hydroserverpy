from typing import TYPE_CHECKING
from .base import HydroServerEndpoint
from ..schemas import Unit

if TYPE_CHECKING:
    from ..service import HydroServer


class UnitEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with Unit entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `Unit`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'units'`.
    """

    def __init__(self, service: 'HydroServer'):
        """
        Initialize the UnitEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = Unit
        self._api_route = self._service.api_route
        self._endpoint_route = 'units'
