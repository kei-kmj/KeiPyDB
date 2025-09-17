from abc import ABC

from db.index.index import Index
from db.query.constant import Constant
from db.query.scan import Scan


class IndexJoinScan(Scan, ABC):

    def __init__(self, left_scan: Scan, index: Index, join_field: str, right_scan: Scan) -> None:
        self.left_scan = left_scan
        self.index = index
        self.join_field = join_field
        self.right_scan = right_scan
        self.before_first()

    def before_first(self) -> None:
        self.left_scan.before_first()

        if not self.left_scan.next():
            return

        self.left_scan.next()
        self.reset_index()

    def next(self) -> bool:
        while True:
            if self.right_scan.next():
                return True
            if not self.left_scan.next():
                return False
            self.reset_index()

    def get_int(self, field_name: str) -> int:
        if self.right_scan.has_field(field_name):
            return self.right_scan.get_int(field_name)
        else:
            return self.left_scan.get_int(field_name)

    def get_value(self, field_name: str) -> Constant:
        if self.right_scan.has_field(field_name):
            return self.right_scan.get_value(field_name)
        else:
            return self.left_scan.get_value(field_name)

    def get_string(self, field_name: str) -> str:
        if self.right_scan.has_field(field_name):
            return self.right_scan.get_string(field_name)
        else:
            return self.left_scan.get_string(field_name)

    def has_field(self, field_name: str) -> bool:
        return self.right_scan.has_field(field_name) or self.left_scan.has_field(field_name)

    def close(self) -> None:
        self.left_scan.close()
        self.right_scan.close()
        self.index.close()

    def reset_index(self) -> None:
        search_key = self.left_scan.get_value(self.join_field)
        self.index.before_first(search_key)
