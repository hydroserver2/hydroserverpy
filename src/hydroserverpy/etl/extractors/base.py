from abc import ABC, abstractmethod


class Extractor(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
