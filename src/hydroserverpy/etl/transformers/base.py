from abc import ABC, abstractmethod


class Transformer(ABC):
    @abstractmethod
    def transform(self) -> None:
        pass

    @property
    @abstractmethod
    def needs_datastreams(self) -> bool:
        False
