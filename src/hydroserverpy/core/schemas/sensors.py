from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from hydroserverpy.core.schemas.base import HydroServerCoreModel


class SensorFields(BaseModel):
    name: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The name of the sensor.'
    )
    description: str = Field(
        strip_whitespace=True,
        description='A description of the sensor.'
    )
    encoding_type: str = Field(
        ..., strip_whitespace=True, max_length=255,
        description='The encoding type of the sensor.'
    )
    manufacturer: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='The manufacturer of the sensor.'
    )
    model: Optional[str] = Field(
        None, strip_whitespace=True, max_length=255,
        description='The model of the sensor.'
    )
    model_link: Optional[str] = Field(
        None, strip_whitespace=True, max_length=500,
        description='A link to a website or file that describes the sensor model.'
    )
    method_type: str = Field(
        ..., strip_whitespace=True, max_length=100,
        description='The type of method used by this sensor to collect observations.'
    )
    method_link: Optional[str] = Field(
        None, strip_whitespace=True, max_length=500,
        description='A link to a website or file that describes the sensor method.'
    )
    method_code: Optional[str] = Field(
        None, strip_whitespace=True, max_length=50,
        description='A code representing the sensor method.'
    )

    model_config = ConfigDict(protected_namespaces=())


class Sensor(HydroServerCoreModel, SensorFields):
    """
    A model representing a sensor, extending the core functionality of HydroServerCoreModel with additional
    fields defined in SensorFields.
    """

    pass
