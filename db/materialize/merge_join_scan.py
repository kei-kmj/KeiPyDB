from abc import ABC
from typing import Optional

from db.materialize.sort_scan import SortScan
from db.query.constant import Constant
from db.query.scan import Scan


class MergeJoinScan(Scan, ABC):

    def __init__(self, left_scan: SortScan, right_scan: SortScan, field_name_left: str, field_name_right: str) -> None:
        self.left_scan = left_scan
        self.right_scan = right_scan
        self.field_name_left = field_name_left
        self.field_name_right = field_name_right
        self.join_value: Optional[Constant] = None
        self.before_first()

    def close(self) -> None:
        self.left_scan.close()
        self.right_scan.close()

    def before_first(self) -> None:
        self.left_scan.before_first()
        self.right_scan.before_first()

    def next(self) -> bool:

        has_more_second = self.right_scan.next()
        if has_more_second and self.left_scan.get_value(self.field_name_left) == self.join_value:
            return True

        has_more_first = self.left_scan.next()
        if has_more_first and self.right_scan.get_value(self.field_name_right) == self.join_value:
            self.right_scan.restore_position()
            return True

        while has_more_first and has_more_second:
            value_first = self.left_scan.get_value(self.field_name_left)
            value_second = self.right_scan.get_value(self.field_name_right)

            if value_first < value_second:
                has_more_first = self.left_scan.next()
            elif value_first > value_second:
                has_more_second = self.right_scan.next()
            else:
                self.right_scan.save_position()
                self.join_value = self.right_scan.get_value(self.field_name_right)
                return True

        return False

    def get_int(self, field_name: str) -> int:
        if self.left_scan.has_field(field_name):
            return self.left_scan.get_int(field_name)

        return self.right_scan.get_int(field_name)

    def get_string(self, field_name: str) -> str:

        if self.left_scan.has_field(field_name):
            return self.left_scan.get_string(field_name)

        return self.right_scan.get_string(field_name)

    def get_value(self, field_name: str) -> Constant:
        if self.left_scan.has_field(field_name):
            return self.left_scan.get_value(field_name)

        return self.right_scan.get_value(field_name)

    def has_field(self, field_name: str) -> bool:
        return self.left_scan.has_field(field_name) or self.right_scan.has_field(field_name)
