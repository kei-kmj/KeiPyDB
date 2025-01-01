from abc import ABC

from db.index.index import Index
from db.query.constant import Constant
from db.query.scan import Scan
from db.record.table_scan import TableScan


class IndexSelectScan(Scan, ABC):
    def __init__(self, table_scan: TableScan, index: Index, val: Constant) -> None:
        self.table_scan = table_scan
        self.index = index
        self.val = val
        self.before_first()

    def before_first(self) -> None:
        self.index.before_first(self.val)

    def next(self) -> bool:
        ok = self.index.next()
        if ok:
            record_id = self.index.get_data_record_id()
            self.table_scan.move_to_rid(record_id)

        return ok

    def get_int(self, field_name: str) -> int:
        return self.table_scan.get_int(field_name)

    def get_string(self, field_name: str) -> str:
        return self.table_scan.get_string(field_name)

    def get_val(self, field_name: str) -> Constant:
        return self.table_scan.get_val(field_name)

    def has_field(self, field_name: str) -> bool:
        return self.table_scan.has_field(field_name)

    def close(self) -> None:
        self.index.close()
        self.table_scan.close()
