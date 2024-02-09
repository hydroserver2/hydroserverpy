from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from hydroserverpy.utils import allow_partial
from hydroserverpy.schemas.users import UserFields


class ObservedPropertyID(BaseModel):
    id: UUID


class ObservedPropertyFields(BaseModel):
    name: str
    definition: str
    description: str = None
    type: str = None
    code: str = None


class ObservedPropertyGetResponse(ObservedPropertyFields, ObservedPropertyID):
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class ObservedPropertyPostBody(ObservedPropertyFields):
    pass


@allow_partial
class ObservedPropertyPatchBody(ObservedPropertyFields):
    pass
