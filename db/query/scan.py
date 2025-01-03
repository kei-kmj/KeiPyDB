from abc import ABC, abstractmethod

from db.query.constant import Constant


class Scan(ABC):

    @abstractmethod
    def before_first(self) -> None:
        pass

    @abstractmethod
    def next(self) -> bool:
        pass

    @abstractmethod
    def get_int(self, field_name: str) -> int:
        pass

    @abstractmethod
    def get_string(self, field_name: str) -> str:
        pass

    @abstractmethod
    def get_value(self, field_name: str) -> Constant:
        pass

    @abstractmethod
    def has_field(self, field_name: str) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
