from threading import Lock

from db.query.update_scan import UpdateScan
from db.record.layout import Layout
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class TempTable:
    _lock = Lock()
    _next_table_num = 0

    @classmethod
    def _next_table_name(cls) -> str:
        with cls._lock:
            cls._next_table_num += 1
            return f"temp{cls._next_table_num}"

    def __init__(self, transaction: Transaction, schema: Schema) -> None:
        self.transaction = transaction
        self.table_name = self._next_table_name()
        self.layout = Layout(schema)

    def open(self) -> UpdateScan:
        return TableScan(self.transaction, self.table_name, self.layout)

    def get_table_name(self) -> str:
        return self.table_name

    def get_layout(self) -> Layout:
        return self.layout
