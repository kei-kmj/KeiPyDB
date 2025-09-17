from abc import ABC

from db.plan.plan import Plan
from db.query.predicate import Predicate
from db.query.scan import Scan
from db.query.select_scan import SelectScan
from db.record.schema import Schema


class SelectPlan(Plan, ABC):
    def __init__(self, plan: Plan, predicate: Predicate) -> None:
        super().__init__()
        self.plan = plan
        self.predicate = predicate

    def open(self) -> Scan:
        scan = self.plan.open()
        return SelectScan(scan, self.predicate)

    def blocks_accessed(self) -> int:
        return self.plan.blocks_accessed()

    def records_output(self) -> int:
        return self.plan.records_output()

    def distinct_values(self, field_name: str) -> int:

        constant = self.predicate.equates_with_constant(field_name)
        if constant is not None:
            return 1
        else:
            base_distinct = self.plan.distinct_values(field_name)
            return max(1, base_distinct // 2)

    def schema(self) -> Schema:
        return self.plan.schema()
