from pydantic import StringConstraints as StrCon
from typing import Annotated
from .base import HydroServerCoreModel


class UnitFields:
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    symbol: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    definition: Annotated[str, StrCon(strip_whitespace=True)]
    type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


class Unit(HydroServerCoreModel, UnitFields):
    """
    A model representing a Unit, extending the core functionality of HydroServerCoreModel with additional
    fields defined in UnitFields.
    """

    pass
