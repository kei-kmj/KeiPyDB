from abc import ABC

from db.query.constant import Constant
from db.query.scan import Scan


class ProjectScan(Scan, ABC):
    def __init__(self, scan: Scan, field_list: list[str]):
        self.scan = scan
        self.field_list = field_list

    def before_first(self) -> None:
        self.scan.before_first()

    def next(self) -> bool:
        return self.scan.next()

    def get_int(self, field_name: str) -> int:
        if self.has_field(field_name):
            return self.scan.get_int(field_name)
        else:
            raise RuntimeError(f"field '{field_name}' not in field_list")

    def get_string(self, field_name: str) -> str:
        if self.has_field(field_name):
            return self.scan.get_string(field_name)
        else:
            raise RuntimeError(f"field '{field_name}' not in field_list")

    def get_val(self, field_name: str) -> int | str | Constant:
        if self.has_field(field_name):
            return self.scan.get_val(field_name)
        else:
            raise RuntimeError(f"field '{field_name}' not in field_list")

    def has_field(self, field_name: str) -> bool:
        return field_name in self.field_list

    def close(self) -> None:
        self.scan.close()
