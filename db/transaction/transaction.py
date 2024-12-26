from threading import Lock

from db.buffer.buffer_manager import BufferManager
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


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
