from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from ..utils import allow_partial
from ..schemas.users import UserFields


class ProcessingLevelID(BaseModel):
    id: UUID


class ProcessingLevelFields(BaseModel):
    code: str
    definition: str = None
    explanation: str = None


class ProcessingLevelGetResponse(ProcessingLevelFields, ProcessingLevelID):
    owner: Optional[str]

    class Config:
        allow_population_by_field_name = True


class ProcessingLevelPostBody(ProcessingLevelFields):

    class Config:
        allow_population_by_field_name = True


@allow_partial
class ProcessingLevelPatchBody(ProcessingLevelFields):
    pass
