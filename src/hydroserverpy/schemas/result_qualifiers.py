from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from hydroserverpy.utils import allow_partial
from hydroserverpy.schemas.users import UserFields


class ResultQualifierID(BaseModel):
    id: UUID


class ResultQualifierFields(BaseModel):
    code: str
    description: str


class ResultQualifierGetResponse(ResultQualifierFields, ResultQualifierID):
    owner: Optional[UserFields]

    class Config:
        allow_population_by_field_name = True


class ResultQualifierPostBody(ResultQualifierFields):
    pass


@allow_partial
class ResultQualifierPatchBody(ResultQualifierFields):
    pass
