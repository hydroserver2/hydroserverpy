from pydantic import BaseModel, Field
from typing import Optional
from hydroserverpy.core.schemas.base import HydroServerCoreModel


class ObservedPropertyFields(BaseModel):
    name: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The name of the observed property.'
    )
    definition: str = Field(
        ..., strip_whitespace=True,
        description='The definition of the observed property.'
    )
    description: Optional[str] = Field(
        None, strip_whitespace=True,
        description='A description of the observed property.'
    )
    type: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='The type of the observed property.'
    )
    code: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='A code representing the observed property.'
    )


class ObservedProperty(HydroServerCoreModel, ObservedPropertyFields):
    """
    A model representing an observed property, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ObservedPropertyFields.
    """

    pass
