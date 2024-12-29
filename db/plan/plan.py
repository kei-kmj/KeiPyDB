import abc
from abc import ABC

from db.query.scan import Scan
from db.record.schema import Schema


class Plan(ABC):

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def open(self) -> Scan:
        """計画の初期化"""
        pass

    @abc.abstractmethod
    def block_accessed(self) -> int:
        pass

    @abc.abstractmethod
    def record_output(self) -> int:
        pass

    @abc.abstractmethod
    def distinct_values(self, field_name: str) -> int:
        """フィールドの値の種類数を返す"""
        pass

    @abc.abstractmethod
    def schema(self) -> Schema:
        """計画のスキーマを返す"""
        pass
