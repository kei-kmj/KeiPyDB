from db.buffer.buffer_manager import BufferManager
from db.log.log_manager import LogManager
from db.transaction.recovery.start_record import StartRecord
from db.transaction.transaction import Transaction


class RecoveryManager:
    def __init__(self, tx:Transaction, tx_number:int, log_manager:LogManager, buffer_manager:BufferManager) -> None:
        self.tx = tx
        self.tx_number = tx_number
        self.log_manager = log_manager
        self.buffer_manager = buffer_manager
        StartRecord.write_to_log(self.log_manager, self.tx_number)
