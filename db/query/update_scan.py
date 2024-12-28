from abc import ABC, abstractmethod

from db.query.constant import Constant
from db.query.scan import Scan


class UpdateScan(Scan, ABC):

    @abstractmethod
    def set_val(self, field_name: str, val: Constant) -> None:
        pass

    @abstractmethod
    def set_int(self, field_name: str, val: int) -> None:
        pass

    @abstractmethod
    def set_string(self, field_name: str, val: str) -> None:
        pass

    @abstractmethod
    def insert(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def get_rid(self) -> int:
        pass

    @abstractmethod
    def move_to_rid(self, rid: int) -> None:
        pass