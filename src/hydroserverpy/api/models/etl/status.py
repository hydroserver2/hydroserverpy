from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Status(BaseModel):
    paused: bool = Field(False)
    last_run_successful: Optional[bool] = Field(None, alias="lastRunSuccessful")
    last_run_message: Optional[str] = Field(None, alias="lastRunMessage")
    last_run: Optional[datetime] = Field(None, alias="lastRun")
    next_run: Optional[datetime] = Field(None, alias="nextRun")

    class Config:
        populate_by_name = True
