from pydantic import BaseModel, Field
from typing import Optional
from hydroserverpy.core.schemas.base import HydroServerCoreModel


class ResultQualifierFields(BaseModel):
    code: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='A code representing the result qualifier.'
    )
    description: Optional[str] = Field(
        None, strip_whitespace=True,
        description='A description of the result qualifier.'
    )


class ResultQualifier(HydroServerCoreModel, ResultQualifierFields):
    """
    A model representing an result qualifier, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ResultQualifierFields.
    """

    pass
