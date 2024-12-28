from abc import ABC

from db.query.constant import Constant
from db.query.predicate import Predicate
from db.query.scan import Scan
from db.query.update_scan import UpdateScan


class SelectScan(UpdateScan, ABC):

    def __init__(self, scan: Scan, predicate: Predicate) -> None:
        self.scan = scan
        self.predicate = predicate

    def before_first(self) -> None:
        self.scan.before_first()

    def next(self) -> bool:
        while self.scan.next():
            if self.predicate.is_satisfied(self):
                return True
        return False

    def get_int(self, field_name: str) -> int:
        return self.scan.get_int(field_name)

    def get_string(self, field_name: str) -> str:
        return self.scan.get_string(field_name)

    def get_val(self, field_name: str) -> int | str | Constant:
        return self.scan.get_val(field_name)

    def has_field(self, field_name: str) -> bool:
        return self.scan.has_field(field_name)

    def close(self) -> None:
        self.scan.close()

    def set_int(self, field_name: str, value: int) -> None:

        if isinstance(self.scan, UpdateScan):
            self.scan.set_int(field_name, value)

    def set_string(self, field_name: str, value: str) -> None:

        if isinstance(self.scan, UpdateScan):
            self.scan.set_string(field_name, value)

    def set_val(self, field_name: str, value: Constant) -> None:
        """値を設定"""
        if isinstance(self.scan, UpdateScan):
            self.scan.set_val(field_name, value)

    def delete(self) -> None:
        """削除"""
        if isinstance(self.scan, UpdateScan):
            self.scan.delete()

    def insert(self) -> None:
        """挿入"""
        if isinstance(self.scan, UpdateScan):
            self.scan.insert()

    def get_rid(self) -> int:
        """RIDを取得"""
        if isinstance(self.scan, UpdateScan):
            return self.scan.get_rid()

        raise TypeError("Underlying scan is not an UpdateScan")

    def move_to_rid(self, record_id: int) -> None:
        """特定のRIDに移動"""
        if isinstance(self.scan, UpdateScan):
            self.scan.move_to_rid(record_id)
