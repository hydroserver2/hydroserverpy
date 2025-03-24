from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field


class Role(BaseModel):
    uid: UUID = Field(..., alias="id")
    name: str = Field(..., max_length=255)
    description: str
    workspace_id: Optional[Union[UUID, str]] = None
