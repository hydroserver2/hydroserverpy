from pydantic import BaseModel, StringConstraints as StrCon
from typing import Optional, Annotated
from .base import HydroServerCoreModel


class ObservedPropertyFields(BaseModel):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    definition: Annotated[str, StrCon(strip_whitespace=True)]
    description: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    type: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None


class ObservedProperty(HydroServerCoreModel, ObservedPropertyFields):
    """
    A model representing an ObservedProperty, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ObservedPropertyFields.
    """

    pass
