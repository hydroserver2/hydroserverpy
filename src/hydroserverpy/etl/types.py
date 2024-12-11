from typing import TypedDict
import pandas as pd


class TimeRange(TypedDict):
    start_time: pd.Timestamp
    end_time: pd.Timestamp
