from pydantic import BaseModel, Field
from typing import Optional, Literal, Union
from pydantic import AnyHttpUrl, conint
from datetime import datetime
from uuid import UUID
from hydroserverpy.utils import allow_partial


class DataSourceID(BaseModel):
    id: UUID


class DataSourceFields(BaseModel):
    name: str
    path: Optional[str]
    url: Optional[AnyHttpUrl]
    header_row: Optional[conint(gt=0)] = Field(None, alias='headerRow')
    data_start_row: Optional[conint(gt=0)] = Field(1, alias='dataStartRow')
    delimiter: Optional[str] = ','
    quote_char: Optional[str] = Field('"', alias='quoteChar')
    interval: Optional[conint(gt=0)]
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']] = \
        Field(None, alias='intervalUnits')
    crontab: Optional[str]
    start_time: Optional[datetime] = Field(None, alias='startTime')
    end_time: Optional[datetime] = Field(None, alias='endTime')
    paused: Optional[bool]
    timestamp_column: Union[conint(gt=0), str] = Field(..., alias='timestampColumn')
    timestamp_format: Optional[str] = Field('%Y-%m-%dT%H:%M:%S%Z', alias='timestampFormat')
    timestamp_offset: Optional[str] = Field('+0000', alias='timestampOffset')
    data_loader_id: UUID = Field(..., alias='dataLoaderId')
    data_source_thru: Optional[datetime] = Field(None, alias='dataSourceThru')
    last_sync_successful: Optional[bool] = Field(None, alias='lastSyncSuccessful')
    last_sync_message: Optional[str] = Field(None, alias='lastSyncMessage')
    last_synced: Optional[datetime] = Field(None, alias='lastSynced')
    next_sync: Optional[datetime] = Field(None, alias='nextSync')


class DataSourceGetResponse(DataSourceFields, DataSourceID):
    pass

    class Config:
        allow_population_by_field_name = True


class DataSourcePostBody(DataSourceFields):
    pass

    class Config:
        allow_population_by_field_name = True


@allow_partial
class DataSourcePatchBody(DataSourceFields):
    pass

    class Config:
        allow_population_by_field_name = True
