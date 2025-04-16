from pydantic import AliasPath
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class OrchestrationConfigurationFields(BaseModel):
    interval: Optional[int] = Field(
        None, gt=0, validation_alias=AliasPath("status", "interval")
    )
    interval_units: Optional[Literal["minutes", "hours", "days"]] = Field(
        None, validation_alias=AliasPath("status", "intervalUnits")
    )
    crontab: Optional[str] = Field(
        None, max_length=255, validation_alias=AliasPath("status", "crontab")
    )
    start_time: Optional[datetime] = Field(
        None, validation_alias=AliasPath("status", "startTime")
    )
    end_time: Optional[datetime] = Field(
        None, validation_alias=AliasPath("status", "endTime")
    )
    last_run_successful: Optional[bool] = Field(
        None, validation_alias=AliasPath("status", "lastRunSuccessful")
    )
    last_run_message: Optional[str] = Field(
        None, max_length=255, validation_alias=AliasPath("status", "lastRunMessage")
    )
    last_run: Optional[datetime] = Field(
        None, validation_alias=AliasPath("status", "lastRun")
    )
    next_run: Optional[datetime] = Field(
        None, validation_alias=AliasPath("status", "nextRun")
    )
    paused: bool = Field(False, validation_alias=AliasPath("status", "paused"))
