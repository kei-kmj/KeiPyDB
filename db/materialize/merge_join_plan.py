from abc import ABC

from db.materialize.merge_join_scan import MergeJoinScan
from db.materialize.sort_plan import SortPlan
from db.materialize.sort_scan import SortScan
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class MergedJoinPlan(Plan, ABC):
    def __init__(
        self,
        transaction: Transaction,
        plan_first: Plan,
        plan_second: Plan,
        field_name_first: str,
        field_name_second: str,
    ) -> None:
        super().__init__()
        self.field_name_first = field_name_first
        self.field_name_second = field_name_second

        self.sort_list_first = [field_name_first]
        self.plan_first = SortPlan(transaction, plan_first, self.sort_list_first)

        self.sort_list_second = [field_name_second]
        self.plan_second = SortPlan(transaction, plan_second, self.sort_list_second)

        self._schema = Schema()
        self._schema.add_all(self.plan_first.schema())
        self._schema.add_all(self.plan_second.schema())

    def open(self) -> Scan:

        scan_first = self.plan_first.open()
        scan_second = self.plan_second.open()

        if not isinstance(scan_second, SortScan) or not isinstance(scan_first, SortScan):
            raise TypeError("Expected SortScan for both scans in MergeJoinScan")

        return MergeJoinScan(scan_first, scan_second, self.field_name_first, self.field_name_second)

    def blocks_accessed(self) -> int:
        return self.plan_first.blocks_accessed() + self.plan_second.blocks_accessed()

    def records_output(self) -> int:
        max_values = max(
            self.plan_first.distinct_values(self.field_name_first),
            self.plan_second.distinct_values(self.field_name_second),
        )
        return self.plan_first.records_output() * self.plan_second.records_output() // max_values

    def distinct_values(self, field_name: str) -> int:

        if self.plan_first.schema().has_field(field_name):
            return self.plan_first.distinct_values(field_name)
        else:
            return self.plan_second.distinct_values(field_name)

    def schema(self) -> Schema:
        return self._schema
