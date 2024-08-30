from pydantic import BaseModel, StringConstraints as StrCon, ConfigDict
from typing import Optional, Annotated
from .base import HydroServerCoreModel


class SensorFields(BaseModel):
    name: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]
    description: Annotated[str, StrCon(strip_whitespace=True)]
    encoding_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    manufacturer: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    model: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    model_link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=500)]] = None
    method_type: Annotated[str, StrCon(strip_whitespace=True, max_length=100)]
    method_link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=500)]] = None
    method_code: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=50)]] = None

    model_config = ConfigDict(protected_namespaces=())


class Sensor(HydroServerCoreModel, SensorFields):
    """
    A model representing a Sensor, extending the core functionality of HydroServerCoreModel with additional
    fields defined in SensorFields.
    """

    pass
