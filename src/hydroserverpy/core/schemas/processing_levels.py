from pydantic import BaseModel, Field
from typing import Optional
from hydroserverpy.core.schemas.base import HydroServerCoreModel


class ProcessingLevelFields(BaseModel):
    code: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='A code representing the processing level.'
    )
    definition: Optional[str] = Field(
        None, strip_whitespace=True,
        description='The definition of the processing level.'
    )
    explanation: Optional[str] = Field(
        None, strip_whitespace=True,
        description='The explanation of the processing level.'
    )


class ProcessingLevel(HydroServerCoreModel, ProcessingLevelFields):
    """
    A model representing a processing level, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ProcessingLevelFields.
    """

    pass
