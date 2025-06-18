from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd


class Loader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def earliest_begin_date(self, payload_mappings) -> str:
        pass
