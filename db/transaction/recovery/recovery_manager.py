from typing import Set

from db.buffer.buffer import Buffer
from db.buffer.buffer_manager import BufferManager
from db.log.log_manager import LogManager
from db.transaction.recovery.commit_record import CommitRecord
from db.transaction.recovery.log_record import LogRecord
from db.transaction.recovery.rollback_record import RollbackRecord
from db.transaction.recovery.set_int_record import SetIntRecord
from db.transaction.recovery.set_string_record import SetStringRecord
from db.transaction.recovery.start_record import StartRecord
from db.transaction.transaction import Transaction


class RecoveryManager:
    def __init__(self, tx: Transaction, tx_number: int, log_manager: LogManager, buffer_manager: BufferManager) -> None:
        self.tx = tx
        self.tx_number = tx_number
        self.log_manager = log_manager
        self.buffer_manager = buffer_manager
        StartRecord.write_to_log(log_manager, tx_number)

    def commit(self) -> None:
        self.buffer_manager.flush_all(self.tx_number)
        lsn = CommitRecord.write_to_log(self.log_manager, self.tx_number)
        self.log_manager.flush(lsn)

    def rollback(self) -> None:
        self._do_rollback()
        self.buffer_manager.flush_all(self.tx_number)
        lsn = RollbackRecord.write_to_log(self.log_manager, self.tx_number)
        self.log_manager.flush(lsn)

    def recover(self) -> None:
        self._do_recover()
        self.buffer_manager.flush_all(self.tx_number)
        lsn = CommitRecord.write_to_log(self.log_manager, self.tx_number)
        self.log_manager.flush(lsn)

    def set_int(self, buffer: Buffer, offset: int) -> int:
        old_value = buffer.contents.get_int(offset)
        block = buffer.block
        return SetIntRecord.write_to_log(self.log_manager, self.tx_number, block, offset, old_value)

    def set_string(self, buffer: Buffer, offset: int) -> int:
        print("offset??", offset)
        old_value = buffer.contents.get_string(offset)
        block = buffer.block
        return SetStringRecord.write_to_log(self.log_manager, self.tx_number, block, offset, old_value)

    def _do_rollback(self) -> None:
        iterator = self.log_manager.iterator()
        for record_data in iterator:
            record = LogRecord.create_log_record(record_data)
            if record.tx_number() == self.tx_number:
                if record.op() == StartRecord.START:
                    return
                record.undo(self.tx)

    def _do_recover(self) -> None:
        finished_transactions: Set[int] = set()
        iterator = self.log_manager.iterator()
        for record_data in iterator:
            record = LogRecord.create_log_record(record_data)
            if record.op() == LogRecord.CHECKPOINT:
                return
            if record.op() in {LogRecord.COMMIT, LogRecord.ROLLBACK}:
                finished_transactions.add(record.tx_number())
            elif record.tx_number() not in finished_transactions:
                record.undo(self.tx)
