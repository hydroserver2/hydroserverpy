from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from hydroserverpy.utils import allow_partial
from hydroserverpy.schemas.users import UserFields


class SensorID(BaseModel):
    id: UUID


class SensorFields(BaseModel):
    name: str
    description: str
    encoding_type: str = Field(alias="encodingType")
    manufacturer: str = None
    model: str = None
    model_link: str = Field(None, alias='modelLink')
    method_type: str = Field(alias='methodType')
    method_link: str = Field(None, alias='methodLink')
    method_code: str = Field(None, alias='methodCode')


class SensorGetResponse(SensorFields, SensorID):
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class SensorPostBody(SensorFields):

    class Config:
        allow_population_by_field_name = True


@allow_partial
class SensorPatchBody(SensorFields):
    pass
