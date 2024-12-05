from typing import TypedDict
import pandas as pd


class TimeRange(TypedDict):
    start_date: pd.Timestamp
    end_date: pd.Timestamp
