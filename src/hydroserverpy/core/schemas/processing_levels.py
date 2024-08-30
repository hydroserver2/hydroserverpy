from pydantic import BaseModel, StringConstraints as StrCon
from typing import Optional, Annotated
from .base import HydroServerCoreModel


class ProcessingLevelFields(BaseModel):
    code: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    definition: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    explanation: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None


class ProcessingLevel(HydroServerCoreModel, ProcessingLevelFields):
    """
    A model representing an ProcessingLevel, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ProcessingLevelFields.
    """

    pass
