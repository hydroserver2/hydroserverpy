from pydantic import Field
from hydroserverpy.core.schemas.base import HydroServerCoreModel


class UnitFields:
    name: str = Field(
        ..., strip_whitespace=True, max_length=255, description="The name of the unit."
    )
    symbol: str = Field(
        ...,
        strip_whitespace=True,
        max_length=255,
        description="The symbol of the unit.",
    )
    definition: str = Field(
        ..., strip_whitespace=True, description="The definition of the unit."
    )
    type: str = Field(
        ..., strip_whitespace=True, max_length=255, description="The type of the unit."
    )


class Unit(HydroServerCoreModel, UnitFields):
    """
    A model representing a unit, extending the core functionality of HydroServerCoreModel with additional
    fields defined in UnitFields.
    """

    pass
