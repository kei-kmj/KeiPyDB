from db.buffer.buffer_manager import BufferManager
from db.file.file_manager import FileManager
from db.log import log_manager


class Transaction:
    def __init__(self, file_manager: FileManager, buffer_manager: BufferManager) -> None:
        self.file_manager = file_manager
        self.buffer_manager = buffer_manager
        self.tx_num = self.next_tx_number()
        self.recovery_manager = RecoveryManager(self, tx_number, log_manager, buffer_manager)


    @staticmethod
    def next_tx_number() -> int:
        with Transaction.lock:
            Transaction.next_tx_number += 1
            return Transaction.next_tx_number

