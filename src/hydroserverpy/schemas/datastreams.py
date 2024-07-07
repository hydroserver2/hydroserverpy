from pydantic import BaseModel, Field
from typing import Union, Literal, Optional
from uuid import UUID
from datetime import datetime
from hydroserverpy.utils import allow_partial


class DatastreamID(BaseModel):
    id: UUID


class DatastreamFields(BaseModel):
    name: Union[UUID, str]
    description: str
    observation_type: str = Field(..., alias='observationType')
    sampled_medium: str = Field(..., alias='sampledMedium')
    no_data_value: float = Field(..., alias='noDataValue')
    aggregation_statistic: str = Field(..., alias='aggregationStatistic')
    time_aggregation_interval: float = Field(..., alias='timeAggregationInterval')
    status: str = None
    result_type: str = Field(..., alias='resultType')
    value_count: int = Field(None, alias='valueCount')
    intended_time_spacing: float = Field(None, alias='intendedTimeSpacing')
    phenomenon_begin_time: datetime = Field(None, alias='phenomenonBeginTime')
    phenomenon_end_time: datetime = Field(None, alias='phenomenonEndTime')
    result_begin_time: datetime = Field(None, alias='resultBeginTime')
    result_end_time: datetime = Field(None, alias='resultEndTime')
    data_source_id: UUID = Field(None, alias='dataSourceId')
    data_source_column: str = Field(None, alias='dataSourceColumn')
    is_visible: bool = Field(True, alias='isVisible')
    thing_id: UUID = Field(..., alias='thingId')
    sensor_id: UUID = Field(..., alias='sensorId')
    observed_property_id: UUID = Field(..., alias='observedPropertyId')
    processing_level_id: UUID = Field(..., alias='processingLevelId')
    unit_id: UUID = Field(..., alias='unitId')
    time_aggregation_interval_units: Literal['seconds', 'minutes', 'hours', 'days'] = \
        Field(..., alias='timeAggregationIntervalUnits')
    intended_time_spacing_units: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = \
        Field(None, alias='intendedTimeSpacingUnits')


class DatastreamGetResponse(DatastreamFields, DatastreamID):

    class Config:
        allow_population_by_field_name = True


class DatastreamPostBody(DatastreamFields):

    class Config:
        allow_population_by_field_name = True


@allow_partial
class DatastreamPatchBody(DatastreamFields):
    thing_id: UUID = Field(..., alias='thingId')
