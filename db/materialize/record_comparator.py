from db.parse.query_data import OrderByField
from db.query.constant import Constant
from db.query.scan import Scan


class _Reverse:
    def __init__(self, value: Constant) -> None:
        self.value = value

    def __lt__(self, other: "_Reverse") -> bool:
        return self.value > other.value

    def __gt__(self, other: "_Reverse") -> bool:
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Reverse):
            return NotImplemented
        return self.value == other.value


class RecordComparator:
    def __init__(self, sort_fields: list[OrderByField]) -> None:
        self.sort_fields = sort_fields

    def compare(self, scan_first: Scan, scan_second: Scan) -> int:

        for order_by_field in self.sort_fields:
            val_first = scan_first.get_value(order_by_field.field_name)
            val_second = scan_second.get_value(order_by_field.field_name)

            if val_first < val_second:
                return -1
            elif val_first > val_second:
                return 1

        return 0

    def compare_row(self, row: dict[str, Constant | list[float]]) -> tuple[Constant | _Reverse, ...]:
        result = []
        for f in self.sort_fields:
            val = row[f.field_name]
            if isinstance(val, list):
                continue
            result.append(val if f.ascending else _Reverse(val))
        return tuple(result)
