from abc import ABC, abstractmethod

from db.query.scan import Scan
from db.record.schema import Schema


class Plan(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def open(self) -> Scan:
        """計画の初期化"""
        pass

    @abstractmethod
    def blocks_accessed(self) -> int:
        pass

    @abstractmethod
    def records_output(self) -> int:
        pass

    @abstractmethod
    def distinct_values(self, field_name: str) -> int:
        """フィールドの値の種類数を返す"""
        pass

    @abstractmethod
    def schema(self) -> Schema:
        """計画のスキーマを返す"""
        pass
