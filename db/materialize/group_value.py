
from db.query.constant import Constant
from db.query.scan import Scan


class GroupValue:
    def __init__(self, scan: Scan, group_fields: list[str]) -> None:
        self.values: dict[str, Constant] = {}

        for field_name in group_fields:
            self.values[field_name] = scan.get_value(field_name)

    def get_value(self, field_name: str) -> Constant:

        if field_name not in self.values:
            raise KeyError(f"Field {field_name} not found in group values")

        return self.values[field_name]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GroupValue):
            return False

        return self.values == other.values

    def __hash__(self) -> int:
        return sum([hash(value) for value in self.values.values()])
