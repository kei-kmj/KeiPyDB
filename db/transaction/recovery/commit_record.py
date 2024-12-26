from db.constants import ByteSize, LogRecordFields
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction


class CommitRecord:
    COMMIT = 3

    def __init__(self, page: Page) -> None:
        self.tx_num = page.get_int(ByteSize.Int)

    @staticmethod
    def op() -> int:
        return CommitRecord.COMMIT

    def tx_number(self) -> int:
        return self.tx_num

    def undo(self, tx: Transaction) -> None:
        pass

    def __str__(self) -> str:
        return f"<COMMIT {self.tx_num}>"

    @staticmethod
    def write_to_log(log_manager: LogManager, tx_number: int) -> int:
        rec = bytearray(LogRecordFields.Two_Fields * ByteSize.Int)
        page = Page(rec)
        page.set_int(0, CommitRecord.COMMIT)
        page.set_int(ByteSize.Int, tx_number)
        return log_manager.append(rec)
