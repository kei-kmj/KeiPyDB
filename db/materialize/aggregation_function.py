from abc import ABC, abstractmethod

from db.query.constant import Constant
from db.query.scan import Scan


class AggregationFunction(ABC):

    @abstractmethod
    def process_first(self, scan: Scan) -> None:
        pass

    @abstractmethod
    def process_next(self, scan: Scan) -> None:
        pass

    @abstractmethod
    def field_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self) -> Constant:
        pass
