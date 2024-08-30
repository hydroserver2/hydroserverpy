from pydantic import BaseModel, StringConstraints as StrCon
from typing import Optional, Annotated
from .base import HydroServerCoreModel


class ResultQualifierFields(BaseModel):
    code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]
    description: Optional[Annotated[str, StrCon(strip_whitespace=True)]]


class ResultQualifier(HydroServerCoreModel, ResultQualifierFields):
    """
    A model representing an ResultQualifier, extending the core functionality of HydroServerCoreModel with additional
    fields defined in ResultQualifierFields.
    """

    pass
