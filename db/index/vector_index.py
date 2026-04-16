from abc import ABC, abstractmethod

from db.query.vector import Vector
from db.record.record_id import RecordID


class VectorIndex(ABC):

    @abstractmethod
    def insert(self, vector: Vector, data_record_id: RecordID) -> None:
        pass

    @abstractmethod
    def search(self, data_value: Vector, k: int) -> list[RecordID]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
