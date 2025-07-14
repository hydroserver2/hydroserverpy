from typing import Optional, Union, List, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field
from ..base import HydroServerCollectionModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer


class Role(BaseModel):
    uid: UUID = Field(..., alias="id")
    name: str = Field(..., max_length=255)
    description: str
    workspace_id: Optional[Union[UUID, str]] = None


class RoleCollection(HydroServerCollectionModel):
    data: List[Role]

    def __init__(
        self,
        _connection: "HydroServer",
        **data,
    ):
        super().__init__(
            _connection=_connection, _model_ref="roles", **data
        )
