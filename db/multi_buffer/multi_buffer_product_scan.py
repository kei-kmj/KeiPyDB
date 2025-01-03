from abc import ABC
from typing import Optional

from db.multi_buffer.buffer_needs import BufferNeeds
from db.multi_buffer.chunk_scan import ChunkScan
from db.query.constant import Constant
from db.query.product_scan import ProductScan
from db.query.scan import Scan
from db.record.layout import Layout
from db.transaction.transaction import Transaction


class MultiBufferProductScan(Scan, ABC):
    NO_BLOCKS = 0

    def __init__(self, transaction: Transaction, left_scan: Scan, table_name: str, layout: Layout) -> None:
        self.transaction = transaction
        self.left_scan = left_scan
        self.table_name = table_name + ".tbl"
        self.layout = layout
        self.file_size = self.transaction.available_buffers()
        self.available = self.transaction.available_buffers()
        self.chunk_size = BufferNeeds.best_factor(self.available, self.file_size)
        self.next_block_number = self.NO_BLOCKS
        self.right_scan: Optional[Scan] = None
        self.product_scan: Optional[ProductScan] = None
        self.before_first()

    def before_first(self) -> None:
        self._use_next_chunk()

    def next(self) -> bool:
        while self.product_scan and not self.product_scan.next():
            if not self._use_next_chunk():
                return False

        return True

    def close(self) -> None:
        if self.right_scan:
            self.right_scan.close()
        if self.product_scan:
            self.product_scan.close()

    def get_value(self, field_name: str) -> Constant:
        if self.product_scan:
            return self.product_scan.get_value(field_name)

        raise RuntimeError("No scan open")

    def get_int(self, field_name: str) -> int:
        if self.product_scan:
            return self.product_scan.get_int(field_name)

        raise RuntimeError("No scan open")

    def get_string(self, field_name: str) -> str:
        if self.product_scan:
            return self.product_scan.get_string(field_name)

        raise RuntimeError("No scan open")

    def has_field(self, field_name: str) -> bool:
        if self.product_scan:
            return self.product_scan.has_field(field_name)

        return False

    def _use_next_chunk(self) -> bool:
        if self.next_block_number >= self.file_size:
            return False

        if self.right_scan:
            self.right_scan.close()

        end_block = min(self.next_block_number + self.chunk_size - 1, self.file_size - 1)
        self.right_scan = ChunkScan(self.transaction, self.table_name, self.layout, self.next_block_number, end_block)
        self.left_scan.before_first()
        self.product_scan = ProductScan(self.left_scan, self.right_scan)
        self.next_block_number = end_block + 1

        return True
