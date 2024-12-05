from abc import ABC, abstractmethod
from pandas import DataFrame
from typing import Dict
import pandas as pd


class Loader(ABC):
    @abstractmethod
    def load(self, df: DataFrame) -> None:
        pass

    @abstractmethod
    def get_data_requirements(self, df: DataFrame) -> Dict[str, pd.Timestamp]:
        pass
