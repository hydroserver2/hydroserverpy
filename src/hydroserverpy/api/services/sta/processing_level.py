from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from ..base import EndpointService
from hydroserverpy.api.models import ProcessingLevel


if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import Workspace, Thing, Datastream


class ProcessingLevelService(EndpointService):
    def __init__(self, connection: "HydroServer"):
        self._model = ProcessingLevel
        self._api_route = "api/data"
        self._endpoint_route = "processing-levels"

        super().__init__(connection)

    def list(
        self,
        workspace: Optional[Union["Workspace", UUID, str]] = None,
        thing: Optional[Union["Thing", UUID, str]] = None,
        datastream: Optional[Union["Datastream", UUID, str]] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List["ProcessingLevel"]:
        """Fetch a collection of processing levels."""

        params = {}

        if workspace is not None:
            params["workspace"] = str(getattr(workspace, "uid", workspace))
        if thing is not None:
            params["thing"] = str(getattr(thing, "uid", thing))
        if datastream is not None:
            params["datastream"] = str(getattr(datastream, "uid", datastream))

        pagination = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
        }

        return super()._list(params=params, pagination=pagination)

    def get(self, uid: Union[UUID, str]) -> "ProcessingLevel":
        """Get a processing level by ID."""

        return super()._get(uid=str(uid))

    def create(
        self,
        workspace: Union["Workspace", UUID, str],
        code: str,
        definition: Optional[str] = None,
        explanation: Optional[str] = None,
    ) -> "ProcessingLevel":
        """Create a new processing level."""

        kwargs = {
            "code": code,
            "definition": definition,
            "explanation": explanation,
            "workspaceId": str(getattr(workspace, "uid", workspace)),
        }

        return super()._create(**kwargs)

    def update(
        self,
        uid: Union[UUID, str],
        code: str = ...,
        definition: Optional[str] = ...,
        explanation: Optional[str] = ...,
    ) -> "ProcessingLevel":
        """Update a processing level."""

        kwargs = {
            "code": code,
            "definition": definition,
            "explanation": explanation,
        }

        return super()._update(
            uid=str(uid), **{k: v for k, v in kwargs.items() if v is not ...}
        )

    def delete(self, uid: Union[UUID, str]) -> None:
        """Delete a processing level."""

        super()._delete(uid=str(uid))
