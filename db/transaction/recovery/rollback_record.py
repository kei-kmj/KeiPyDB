from db.constants import LogRecordFields, ByteSize
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction


class RollbackRecord:
    ROLLBACK = 1
    def __init__(self, page: Page) -> None:
        self.tx_number = page.get_int(ByteSize.Int)

    def op(self) -> int:
        return self.ROLLBACK

    def tx_number(self) -> int:
        return self.tx_number

    def undo(self, tx: Transaction) -> None:
        pass

    def __str__(self) -> str:
        return f"<ROLLBACK {self.tx_number}>"


    @staticmethod
    def write_to_log(log_manager: LogManager, tx_number:int) -> int:
        rec = bytearray(LogRecordFields.TWO_FIELDS * ByteSize.Int)
        page = Page(rec)
        page.set_int(0, RollbackRecord.ROLLBACK)
        page.set_int(ByteSize.Int, tx_number)
        return log_manager.append(rec)
