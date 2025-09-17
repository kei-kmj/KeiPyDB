from abc import ABC
from typing import Optional

from db.materialize.aggregation_function import AggregationFunction
from db.materialize.group_value import GroupValue
from db.query.constant import Constant
from db.query.scan import Scan


class GroupByScan(Scan, ABC):

    def __init__(self, scan: Scan, group_fields: list[str], agg_fns: list[AggregationFunction]) -> None:
        self.scan = scan
        self.group_fields = group_fields
        self.agg_fns = agg_fns
        self.group_value: Optional[GroupValue] = None
        self.more_groups = False
        self.before_first()

    def before_first(self) -> None:
        self.scan.before_first()
        self.more_groups = self.scan.next()

    def next(self) -> bool:

        for agg_fn in self.agg_fns:
            agg_fn.process_first(self.scan)

        self.group_value = GroupValue(self.scan, self.group_fields)

        while True:
            self.more_groups = self.scan.next()
            if not self.more_groups:
                break
            current_group_value = GroupValue(self.scan, self.group_fields)

            if not self.group_value.__eq__(current_group_value):
                break

            for agg_fn in self.agg_fns:
                agg_fn.process_next(self.scan)

        return True

    def close(self) -> None:
        self.scan.close()

    def get_value(self, field_name: str) -> Constant:

        if not self.group_value:
            raise RuntimeError("No group value set yet")

        if field_name in self.group_fields:
            return self.group_value.get_value(field_name)

        for agg_fn in self.agg_fns:
            if field_name == agg_fn.field_name():
                return agg_fn.get_value()

        raise RuntimeError(f"Field {field_name} not found")

    def get_int(self, field_name: str) -> int:
        return self.get_value(field_name).as_int()

    def get_string(self, field_name: str) -> str:
        return self.get_value(field_name).as_string()

    def has_field(self, field_name: str) -> bool:
        if field_name in self.group_fields:
            return True

        for agg_fn in self.agg_fns:
            if field_name == agg_fn.field_name():
                return True

        return False
