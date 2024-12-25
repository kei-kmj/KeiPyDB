from db.constants import ByteSize, LogRecordFields
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction


class CheckpointRecord:
    CHECKPOINT = 2

    def __init__(self) -> None:
        pass

    def __copy__(self) -> int:
        return self.CHECKPOINT

    @staticmethod
    def tx_number() -> int:
        return -1

    def undo(self, tx: Transaction) -> None:
        pass

    def __str__(self) -> str:
        return "<CHECKPOINT>"

    @staticmethod
    def write_to_log(log_manager: LogManager) -> int:
        rec = bytearray(LogRecordFields.ONE_FIELD * ByteSize.Int)
        page = Page(rec)
        page.set_int(0, CheckpointRecord.CHECKPOINT)
        return log_manager.append(rec)
