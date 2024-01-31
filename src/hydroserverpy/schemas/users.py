from pydantic import BaseModel, Field


class OrganizationFields(BaseModel):
    code: str
    name: str
    description: str = None
    type: str
    link: str = None

    @classmethod
    def is_empty(cls, obj):
        return not (obj.name and obj.code and obj.type)


class UserFields(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str = None
    middle_name: str = Field(default=None, alias="middleName")
    phone: str = None
    address: str = None
    type: str = None
    link: str = None
    organization: OrganizationFields = None

    class Config:
        allow_population_by_field_name = True
