from pydantic import BaseModel
from uuid import UUID
from hydroserverpy.utils import allow_partial


class DataLoaderID(BaseModel):
    id: UUID


class DataLoaderFields(BaseModel):
    name: str


class DataLoaderGetResponse(DataLoaderFields, DataLoaderID):
    pass

    class Config:
        allow_population_by_field_name = True


class DataLoaderPostBody(DataLoaderFields):
    pass


@allow_partial
class DataLoaderPatchBody(DataLoaderFields):
    pass
