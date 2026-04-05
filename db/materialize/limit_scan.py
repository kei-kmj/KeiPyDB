from db.query.constant import Constant
from db.query.scan import Scan


class LimitScan(Scan):
    def __init__(self, scan: Scan, limit: int) -> None:
        super().__init__()
        self.scan = scan
        self.limit = limit
        self.count = 0

    def before_first(self) -> None:
        self.scan.before_first()
        self.count = 0

    def next(self) -> bool:
        if self.count >= self.limit:
            return False

        self.count += 1
        return self.scan.next()

    def get_int(self, field_name: str) -> int:
        return self.scan.get_int(field_name)

    def get_string(self, field_name: str) -> str:
        return self.scan.get_string(field_name)

    def get_vector(self, field_name: str) -> list[float]:
        return self.scan.get_vector(field_name)

    def get_value(self, field_name: str) -> Constant:
        return self.scan.get_value(field_name)

    def has_field(self, field_name: str) -> bool:
        return self.scan.has_field(field_name)

    def close(self) -> None:
        self.scan.close()
