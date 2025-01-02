from abc import ABC, abstractmethod


class AggregationFunction(ABC):

    @abstractmethod
    def process_first(self, val: int) -> None:
        pass

    @abstractmethod
    def process_next(self, val: int) -> None:
        pass

    @abstractmethod
    def field_name(self) -> str:
        pass

    @abstractmethod
    def value(self) -> int:
        pass
