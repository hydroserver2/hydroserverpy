from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd


class Loader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_data_requirements(self, df: pd.DataFrame) -> Dict[str, pd.Timestamp]:
        pass
