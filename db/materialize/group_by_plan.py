from abc import ABC

from db.materialize.aggregation_function import AggregationFunction
from db.materialize.group_by_scan import GroupByScan
from db.materialize.sort_plan import SortPlan
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class GroupByPlan(Plan, ABC):

    def __init__(
        self, transaction: Transaction, plan: Plan, group_fields: list[str], agg_fns: list[AggregationFunction]
    ) -> None:
        super().__init__()
        self.transaction = transaction
        self.plan = SortPlan(transaction, plan, group_fields)
        self.group_fields = group_fields
        self.agg_fns = agg_fns
        self._schema = Schema()

        for field_name in group_fields:
            self._schema.add(field_name, self.plan.schema())

        for agg_fn in agg_fns:
            self._schema.add_int_field(agg_fn.field_name())

    def open(self) -> Scan:

        sorted_scan = self.plan.open()
        return GroupByScan(sorted_scan, self.group_fields, self.agg_fns)

    def blocks_accessed(self) -> int:
        return self.plan.blocks_accessed()

    def records_output(self) -> int:

        num_groups = 1
        for field_name in self.group_fields:
            num_groups *= self.plan.distinct_values(field_name)
        return num_groups

    def distinct_values(self, field_name: str) -> int:

        if self.plan.schema().has_field(field_name):
            return self.plan.distinct_values(field_name)

        return self.records_output()

    def schema(self) -> Schema:
        return self._schema
