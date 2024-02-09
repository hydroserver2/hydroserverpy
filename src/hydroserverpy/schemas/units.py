from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from hydroserverpy.utils import allow_partial
from hydroserverpy.schemas.users import UserFields


class UnitID(BaseModel):
    id: UUID


class UnitFields(BaseModel):
    name: str
    symbol: str
    definition: str
    type: str


class UnitGetResponse(UnitFields, UnitID):
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class UnitPostBody(UnitFields):
    pass


@allow_partial
class UnitPatchBody(UnitFields):
    pass
