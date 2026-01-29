from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def earliest_begin_date(self, task_mappings) -> str:
        pass
