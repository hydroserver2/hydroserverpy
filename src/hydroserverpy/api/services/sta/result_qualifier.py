from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import ResultQualifier


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace


class ResultQualifierService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = ResultQualifier
        self._api_route = "api/data"
        self._endpoint_route = "result-qualifiers"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["ResultQualifier"]:
        """Fetch a collection of result qualifiers."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(self, uid: Union[UUID, str]) -> "ResultQualifier":
        """Get a result qualifier by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        code: str,
        description: str,
    ) -> "ResultQualifier":
        """Create a new result qualifier."""

        kwargs = {
            "code": code,
            "description": description,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        code: str = ...,
        description: str = ...,
    ) -> "ResultQualifier":
        """Update a result qualifier."""

        kwargs = {
            "code": code,
            "description": description,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a result qualifier."""

        super()._delete(uid=str(uid))
