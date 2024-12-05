from abc import ABC, abstractmethod
from typing import Dict
from ..types import TimeRange


class Extractor(ABC):
    @abstractmethod
    def prepare_params(self, data_requirements: Dict[str, TimeRange]):
        pass

    @abstractmethod
    def extract(self):
        pass
