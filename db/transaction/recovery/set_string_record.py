from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction


class SetStringRecord:
    SET_STRING = 5

    def __init__(self, page: Page) -> None:
        tx_pos = ByteSize.Int
        self._tx_number = page.get_int(tx_pos)
        file_name_pos = tx_pos + ByteSize.Int
        file_name = page.get_string(file_name_pos)
        block_pos = file_name_pos + Page.get_max_length(len(file_name))
        block_number = page.get_int(block_pos)
        self.block = BlockID(file_name, block_number)

        offset_pos = block_pos + ByteSize.Int
        self.offset = page.get_int(offset_pos)

        value_pos = offset_pos + ByteSize.Int
        self.value = page.get_string(value_pos)

    @staticmethod
    def op() -> int:
        return SetStringRecord.SET_STRING

    def tx_number(self) -> int:
        return self._tx_number

    def undo(self, tx: Transaction) -> None:
        tx.pin(self.block)
        tx.set_string(self.block, self.offset, self.value, False)
        tx.unpin(self.block)

    def __str__(self) -> str:
        return f"<SET_STRING {self._tx_number} {self.block} {self.offset} {self.value}>"

    @staticmethod
    def write_to_log(log_manager: LogManager, tx_number: int, block: BlockID, offset: int, value: str) -> int:
        tx_pos = ByteSize.Int
        file_name_pos = tx_pos + ByteSize.Int
        block_pos = file_name_pos + Page.get_max_length(len(block.file_name))
        offset_pos = block_pos + ByteSize.Int
        value_pos = offset_pos + ByteSize.Int

        rec = bytearray(value_pos + Page.get_max_length(len(value)))
        page = Page(rec)
        page.set_int(0, SetStringRecord.SET_STRING)
        page.set_int(tx_pos, tx_number)
        page.set_string(file_name_pos, block.file_name)
        page.set_int(block_pos, block.block_number)
        page.set_int(offset_pos, offset)
        page.set_string(value_pos, value)

        return log_manager.append(rec)
