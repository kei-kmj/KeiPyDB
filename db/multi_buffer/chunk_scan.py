from abc import ABC
from typing import List

from db.constants import FieldType
from db.file.block_id import BlockID
from db.query.constant import Constant
from db.query.scan import Scan
from db.record.layout import Layout
from db.record.record_page import RecordPage
from db.transaction.transaction import Transaction


class ChunkScan(Scan, ABC):
    INVALID_SLOT = -1

    def __init__(
        self, transaction: Transaction, file_name: str, layout: Layout, start_block: int, end_block: int
    ) -> None:
        super().__init__()
        self.transaction = transaction
        self.file_name = file_name
        self.layout = layout
        self.start_block = start_block
        self.end_block = end_block
        self.current_block = start_block
        self.buffers: List[RecordPage] = []
        self.current_slot = self.INVALID_SLOT
        self.record_page: RecordPage = RecordPage(transaction, BlockID(file_name, start_block), layout)

        inclusive_end_block = end_block + 1

        for block_number in range(start_block, inclusive_end_block):
            block = BlockID(file_name, block_number)
            self.buffers.append(RecordPage(transaction, block, layout))

        self._move_to_block(start_block)

    def close(self) -> None:
        for i in range(len(self.buffers)):
            block = BlockID(self.file_name, self.start_block + i)
            self.transaction.unpin(block)

    def before_first(self) -> None:
        self._move_to_block(self.start_block)

    def next(self) -> bool:

        self.current_slot = self.record_page.next_after(self.current_slot)

        while self.current_slot <= self.INVALID_SLOT:
            if self.current_block == self.end_block:
                return False
            self._move_to_block(self.current_block + 1)
            self.current_slot = self.record_page.next_after(self.current_slot)

        return True

    def get_int(self, field_name: str) -> int:
        return self.record_page.get_int(self.current_slot, field_name)

    def get_string(self, field_name: str) -> str:
        return self.record_page.get_string(self.current_slot, field_name)

    def get_value(self, field_name: str) -> Constant:

        if self.layout.schema.get_type(field_name) == FieldType.Integer:
            return Constant(self.get_int(field_name))
        return Constant(self.get_string(field_name))

    def has_field(self, field_name: str) -> bool:
        return self.layout.schema.has_field(field_name)

    def _move_to_block(self, block_number: int) -> None:
        self.current_block = block_number
        self.record_page = self.buffers[block_number - self.start_block]
        self.current_slot = self.INVALID_SLOT
