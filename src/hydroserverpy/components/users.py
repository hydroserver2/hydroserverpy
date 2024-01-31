from pydantic import BaseModel, Field
from typing import Optional


class Organization(BaseModel):
    code: str
    name: str
    description: Optional[str]
    type: str
    link: Optional[str]


class UserResponse(BaseModel):
    email: str
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    middle_name: Optional[str] = Field(None, alias='middleName')
    phone: Optional[str]
    address: Optional[str]
    type: str
    link: Optional[str]
    organization: Optional[Organization]


class User:

    def __init__(self, service):
        self._service = service
