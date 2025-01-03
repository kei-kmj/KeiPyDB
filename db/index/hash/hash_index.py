from abc import ABC
from typing import Optional

from db.index.index import Index
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class HashIndex(Index, ABC):
    NUM_BUCKETS = 100

    def __init__(self, transaction: Transaction, index_name: str, layout: Layout) -> None:

        self.transaction = transaction
        self.index_name = index_name
        self.layout = layout
        self.search_key: Optional[Constant] = None
        self.table_scan: Optional[TableScan] = None

    def before_first(self, search_key: Constant) -> None:
        self.close()

        if not self.transaction or not self.layout:
            raise RuntimeError("Hash index is not initialized")

        self.search_key = search_key
        bucket = hash(search_key) % self.NUM_BUCKETS
        table_name = f"{self.index_name}{bucket}"

        self.table_scan = TableScan(self.transaction, table_name, self.layout)

    def next(self) -> bool:

        if not self.table_scan:
            raise RuntimeError("Table scan is not initialized")

        while self.table_scan.next():

            if self.search_key is self.table_scan.get_value("data_value"):

                return True
        return False

    def get_data_record_id(self) -> RecordID:
        if not self.table_scan:
            raise RuntimeError("Table scan is not initialized")

        block_number = self.table_scan.get_int("block")
        slot = self.table_scan.get_int("id")

        return RecordID(block_number, slot)

    def insert(self, data_value: Constant, data_record_id: RecordID) -> None:
        if not self.table_scan:
            raise RuntimeError("Table scan is not initialized")

        self.before_first(data_value)
        self.table_scan.insert()
        self.table_scan.set_int("block", data_record_id.block_number)
        self.table_scan.set_int("id", data_record_id.slot)
        self.table_scan.set_val("data_value", data_value)

    def delete(self, data_value: Constant, data_record_id: RecordID) -> None:
        if not self.table_scan:
            raise RuntimeError("Table scan is not initialized")

        self.before_first(data_value)
        print("data_record_id★", self.table_scan.next())
        while self.table_scan.next():
            if data_record_id == self.get_data_record_id():
                self.table_scan.delete()
                return
        raise ValueError("Record not found")

    def close(self) -> None:
        if self.table_scan:
            self.table_scan.close()

    @staticmethod
    def search_cost(num_blocks: int) -> int:
        return num_blocks // HashIndex.NUM_BUCKETS
