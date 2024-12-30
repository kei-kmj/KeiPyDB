from abc import ABC
from typing import cast

from db.metadata.metadata_manager import MetadataManager
from db.parse.create_index import CreateIndex
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.modify_data import ModifyData
from db.plan.plan import Plan
from db.plan.query_planner import QueryPlanner
from db.plan.select_plan import SelectPlan
from db.plan.table_plan import TablePlan
from db.query.scan import Scan
from db.query.update_scan import UpdateScan
from db.transaction.transaction import Transaction


class BasicUpdatePlanner(QueryPlanner, ABC):

    def __init__(self, metadata_manager: MetadataManager):
        self.metadata_manager = metadata_manager

    def execute_delete(self, data: DeleteData, transaction: Transaction) -> int:
        """条件に合うレコードを削除する"""

        plan: Plan = TablePlan(transaction, data.table_name, self.metadata_manager)
        plan = SelectPlan(plan, data.predicate)

        scan = plan.open()
        if not isinstance(scan, UpdateScan):
            raise ValueError("Delete only works on UpdateScan")

        count = 0

        while scan.next():
            scan.delete()
            count += 1

        scan.close()
        return count

    def execute_modify(self, data: ModifyData, transaction: Transaction) -> int:
        """条件に合うレコードを更新する"""
        plan: Plan = TablePlan(transaction, data.table_name, self.metadata_manager)
        plan = SelectPlan(plan, data.predicate)

        scan = plan.open()
        scan = cast(UpdateScan, scan)

        count = 0

        while scan.next():
            value = data.new_value.evaluate(scan)
            scan.set_val(data.get_field_name(), value)
            count += 1

        scan.close()
        return count

    def execute_insert(self, data: InsertData, transaction: Transaction) -> int:
        plan = TablePlan(transaction, data.table_name, self.metadata_manager)
        scan: Scan = plan.open()

        if not isinstance(scan, UpdateScan):
            raise TypeError("Expected UpdateScan, but got {type(scan)}")

        scan.insert()

        fields = data.get_fields()
        values = iter(data.get_values())

        for field_name in fields:
            value = next(values)
            scan.set_val(field_name, value)

        scan.close()
        return 1

    def execute_create_table(self, data: CreateTable, transaction: Transaction) -> int:
        self.metadata_manager.create_table(data.table_name, data.get_schema(), transaction)
        return 0

    def execute_create_view(self, data: CreateView, transaction: Transaction) -> int:
        self.metadata_manager.create_view(data.view_name, data.get_query(), transaction)
        return 0

    def execute_create_index(self, data: CreateIndex, transaction: Transaction) -> int:
        self.metadata_manager.create_index(data.index_name, data.table_name, data.field_name, transaction)
        return 0
