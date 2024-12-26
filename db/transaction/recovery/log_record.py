from abc import ABC, abstractmethod
from typing import Any

from db.file.page import Page
from db.transaction.recovery.checkpoint_record import CheckpointRecord
from db.transaction.recovery.commit_record import CommitRecord
from db.transaction.recovery.rollback_record import RollbackRecord
from db.transaction.recovery.set_int_record import SetIntRecord
from db.transaction.recovery.set_string_record import SetStringRecord
from db.transaction.recovery.start_record import StartRecord
from db.transaction.transaction import Transaction


class LogRecord(ABC):
    CHECKPOINT = 0
    START = 1
    COMMIT = 2
    ROLLBACK = 3
    SET_INT = 4
    SET_STRING = 5

    @abstractmethod
    def op(self) -> int:
        pass

    @abstractmethod
    def tx_number(self) -> int:
        pass

    @abstractmethod
    def undo(self, tx: Transaction) -> None:
        pass

    @classmethod
    def create_log_record(cls, bytes_data: bytes) -> StartRecord | CommitRecord | RollbackRecord | SetIntRecord | SetStringRecord | CheckpointRecord:

        page = Page(bytes_data)
        op_type = page.get_int(0)

        if op_type == LogRecord.CHECKPOINT:
            return CheckpointRecord()
        elif op_type == LogRecord.START:
            return StartRecord(page)
        elif op_type == LogRecord.COMMIT:
            return CommitRecord(page)
        elif op_type == LogRecord.ROLLBACK:
            return RollbackRecord(page)
        elif op_type == LogRecord.SET_INT:
            return SetIntRecord(page)
        elif op_type == LogRecord.SET_STRING:
            return SetStringRecord(page)
        else:
            raise ValueError(f"不明な操作コード: {op_type}")
