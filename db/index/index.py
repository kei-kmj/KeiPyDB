from abc import ABC, abstractmethod

from db.query.constant import Constant
from db.record.record_id import RecordID


class Index(ABC):

    @abstractmethod
    def before_first(self, search_key: Constant) -> None:
        pass

    @abstractmethod
    def next(self) -> bool:
        pass

    @abstractmethod
    def get_data_record_id(self) -> RecordID:
        pass


    @abstractmethod
    def insert(self, data_value: Constant, data_record_id: RecordID) -> None:
        pass

    @abstractmethod
    def delete(self, data_value: Constant, data_record_id: RecordID) -> None:
        pass


    @abstractmethod
    def close(self) -> None:
        pass
