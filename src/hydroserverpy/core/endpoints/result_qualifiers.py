from typing import List, Union, TYPE_CHECKING
from uuid import UUID
from hydroserverpy.core.endpoints.base import HydroServerEndpoint, expand_docstring
from hydroserverpy.core.schemas import ResultQualifier

if TYPE_CHECKING:
    from hydroserverpy.core.service import HydroServer


class ResultQualifierEndpoint(HydroServerEndpoint):
    """
    An endpoint for interacting with result qualifier entities in the HydroServer service.

    :ivar _model: The model class associated with this endpoint, set to `ResultQualifier`.
    :ivar _api_route: The base route of the API, derived from the service.
    :ivar _endpoint_route: The specific route of the endpoint, set to `'result-qualifiers'`.
    """

    def __init__(self, service: 'HydroServer'):
        """
        Initialize the ResultQualifierEndpoint.

        :param service: The HydroServer service instance to use for requests.
        :type service: HydroServer
        """

        super().__init__(service)
        self._model = ResultQualifier
        self._api_route = self._service.api_route
        self._endpoint_route = 'result-qualifiers'

    def list(self) -> List[ResultQualifier]:
        """
        Retrieve a collection of result qualifiers owned by the logged-in user.
        """

        return super()._get()

    @expand_docstring(include_uid=True)
    def get(self, uid: Union[UUID, str]) -> ResultQualifier:
        """
        Retrieve a result qualifier owned by the logged-in user.
        """

        return super()._get(uid)

    @expand_docstring(model=ResultQualifier)
    def create(self, **kwargs) -> ResultQualifier:
        """
        Create a new result qualifier in HydroServer.
        """

        return super()._post(**kwargs)

    @expand_docstring(model=ResultQualifier, include_uid=True)
    def update(self, uid: Union[UUID, str], **kwargs) -> ResultQualifier:
        """
        Update an existing result qualifier in HydroServer.
        """

        return super()._patch(uid=uid, **kwargs)

    @expand_docstring(include_uid=True)
    def delete(self, uid: Union[UUID, str]) -> None:
        """
        Delete an existing result qualifier in HydroServer.
        """

        super()._delete(uid=uid)
