from threading import Lock

from db.buffer.buffer_manager import BufferManager
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.transaction.buffer_list import BufferList
from db.transaction.concurrency.concurrency_manager import ConcurrencyManager


class Transaction:
    _next_tx_number = 0
    _lock = Lock()
    END_OF_FILE = -1

    def __init__(self, file_manager: FileManager, log_manager: LogManager, buffer_manager: BufferManager) -> None:
        from db.transaction.recovery.recovery_manager import RecoveryManager

        self.file_manager = file_manager
        self.buffer_manager = buffer_manager

        with Transaction._lock:
            self.tx_number = Transaction._next_tx_number
            Transaction._next_tx_number += 1

        self.recovery_manager = RecoveryManager(self, self.tx_number, log_manager, buffer_manager)
        self.concurrency_manager = ConcurrencyManager()
        self.buffer_list = BufferList(buffer_manager)

    def commit(self) -> None:
        self.recovery_manager.commit()
        self.concurrency_manager.release()
        self.buffer_list.unpin_all()

    def rollback(self) -> None:
        self.recovery_manager.rollback()
        self.concurrency_manager.release()
        self.buffer_list.unpin_all()
        print(f"Transaction {self.tx_number} rolled back")

    def recover(self) -> None:
        self.recovery_manager.recover()
        self.concurrency_manager.release()

    def pin(self, block: BlockID) -> None:
        self.buffer_list.pin(block)

    def unpin(self, block: BlockID) -> None:
        self.buffer_list.unpin(block)

    def get_int(self, block: BlockID, offset: int) -> int:
        self.concurrency_manager.lock_shared(block)
        buffer = self.buffer_manager.pin(block)
        return buffer.get_contents().get_int(offset)

    def get_string(self, block: BlockID, offset: int) -> str:
        self.concurrency_manager.lock_shared(block)
        buffer = self.buffer_manager.pin(block)
        return buffer.get_contents().get_string(offset)

    def set_int(self, block: BlockID, offset: int, value: int, ok_to_log: bool = True) -> None:
        self.concurrency_manager.lock_exclusive(block)
        buffer = self.buffer_manager.pin(block)
        if not buffer:
            raise ValueError(f"Block {block} not pinned")
        lsn = -1
        if ok_to_log:
            lsn = self.recovery_manager.set_int(buffer, offset)

        buffer.get_contents().set_int(offset, value)
        buffer.set_modified(self.tx_number, lsn)

    def set_string(self, block: BlockID, offset: int, value: str, ok_to_log: bool = False) -> None:
        self.concurrency_manager.lock_exclusive(block)
        buffer = self.buffer_list.get_buffer(block)
        if not buffer:
            raise ValueError(f"Block {block} not pinned")
        lsn = -1
        if ok_to_log:
            lsn = self.recovery_manager.set_string(buffer, offset)
        buffer.get_contents().set_string(offset, value)
        buffer.set_modified(self.tx_number, lsn)

    def size(self, file_name: str) -> int:
        dummy_block = BlockID(file_name, Transaction.END_OF_FILE)
        self.concurrency_manager.lock_shared(dummy_block)
        return self.file_manager.length(file_name)

    def append(self, file_name: str) -> BlockID:
        dummy_block = BlockID(file_name, Transaction.END_OF_FILE)
        self.concurrency_manager.lock_exclusive(dummy_block)
        return self.file_manager.append(file_name)

    def block_size(self) -> int:
        return self.file_manager.block_size

    def available_buffers(self) -> int:
        return self.buffer_manager.available()
