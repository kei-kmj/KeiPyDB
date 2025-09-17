from abc import ABC
from typing import cast

from db.index.query.index_select_scan import IndexSelectScan
from db.metadata.index_info import IndexInfo
from db.plan.plan import Plan
from db.query.constant import Constant
from db.query.scan import Scan
from db.record.schema import Schema
from db.record.table_scan import TableScan


class IndexSelectPlan(Plan, ABC):

    def __init__(self, plan: Plan, index_info: IndexInfo, val: Constant) -> None:
        """インデックス選択計画を作成"""
        super().__init__()
        self.plan = plan
        self.index_info = index_info
        self.val = val

    def open(self) -> Scan:
        scan = self.plan.open()
        table_scan = cast(TableScan, scan)
        index = self.index_info.open()
        return IndexSelectScan(table_scan, index, self.val)

    def blocks_accessed(self) -> int:
        return self.index_info.blocks_accessed() + self.records_output()

    def records_output(self) -> int:
        return self.index_info.records_output()

    def distinct_values(self, field_name: str) -> int:
        return self.index_info.distinct_values(field_name)

    def schema(self) -> Schema:
        return self.plan.schema()
