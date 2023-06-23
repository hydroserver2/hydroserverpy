from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DatastreamStatus(BaseModel):
    file_thru_date: Optional[datetime]
    database_thru_date: Optional[datetime]
    last_sync_successful: Optional[bool]


class FileStreamStatus(BaseModel):
    file_path: str
    valid_conf: Optional[bool]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]
    last_sync_successful: Optional[bool]
    datastreams: Optional[dict[str, DatastreamStatus]]
