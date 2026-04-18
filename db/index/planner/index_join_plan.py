from abc import ABC

from db.index.query.index_join_scan import IndexJoinScan
from db.metadata.index_def import IndexDef
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class IndexJoinPlan(Plan, ABC):

    def __init__(
        self, left_plan: Plan, right_plan: Plan, index_info: IndexDef, join_filed: str, transaction: Transaction
    ) -> None:
        """インデックス結合計画を作成"""
        super().__init__()
        self.left_plan = left_plan
        self.right_plan = right_plan
        self.index_info = index_info
        self.join_filed = join_filed
        self.transaction = transaction
        self._schema = Schema()
        self._schema.add_all(left_plan.schema())
        self._schema.add_all(right_plan.schema())

    def open(self) -> Scan:
        left_scan = self.left_plan.open()

        table_scan = self.right_plan.open()
        index = self.index_info.open(self.transaction)

        return IndexJoinScan(left_scan, index, self.join_filed, table_scan)

    def blocks_accessed(self) -> int:
        return (
            self.left_plan.blocks_accessed()
            + (self.left_plan.records_output() * self.index_info.blocks_accessed(self.transaction))
            + self.records_output()
        )

    def records_output(self) -> int:
        return self.left_plan.records_output() * self.index_info.records_output()

    def distinct_values(self, field: str) -> int:
        if self.left_plan.schema().has_field(field):
            return self.left_plan.distinct_values(field)
        else:
            return self.right_plan.distinct_values(field)

    def schema(self) -> Schema:
        return self._schema
