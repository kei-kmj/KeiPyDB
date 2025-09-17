from abc import ABC
from typing import cast

from db.metadata.metadata_manager import MetadataManager
from db.parse.create_index import CreateIndex
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.modify_data import ModifyData
from db.plan.select_plan import SelectPlan
from db.plan.table_plan import TablePlan
from db.plan.update_planner import UpdatePlanner
from db.query.update_scan import UpdateScan
from db.transaction.transaction import Transaction


class IndexUpdatePlanner(UpdatePlanner, ABC):

    def __init__(self, metadata_manager: MetadataManager) -> None:
        self.metadata_manager = metadata_manager

    def execute_insert(self, data: InsertData, transaction: Transaction) -> int:
        table_name = data.table_name
        plan = TablePlan(transaction, table_name, self.metadata_manager)

        scan = plan.open()
        update_scan = cast(UpdateScan, scan)
        update_scan.insert()
        record_id = update_scan.get_rid()

        indexes = self.metadata_manager.get_index_info(table_name, transaction)
        val_iterator = iter(data.values)
        for field_name in data.fields:
            val = next(val_iterator)
            update_scan.set_value(field_name, val)

            if field_name in indexes:
                index = indexes[field_name].open()
                index.insert(val, record_id)
                index.close()

        update_scan.close()
        return 1

    def execute_delete(self, data: DeleteData, transaction: Transaction) -> int:
        table_name = data.table_name
        table_plan = TablePlan(transaction, table_name, self.metadata_manager)
        plan = SelectPlan(table_plan, data.predicate)

        indexes = self.metadata_manager.get_index_info(table_name, transaction)

        update_scan = cast(UpdateScan, plan.open())
        count = 0
        while update_scan.get_rid():
            record_id = update_scan.get_rid()
            for filed_name, index_info in indexes.items():
                value = update_scan.get_value(filed_name)
                index = index_info.open()
                index.delete(value, record_id)
                index.close()

            update_scan.delete()
            count += 1

        update_scan.close()
        return count

    def execute_modify(self, data: ModifyData, transaction: Transaction) -> int:
        table_name = data.table_name
        target_field = data.field_name

        table_plan = TablePlan(transaction, table_name, self.metadata_manager)
        plan = SelectPlan(table_plan, data.predicate)

        index_info = self.metadata_manager.get_index_info(table_name, transaction).get(target_field)
        index = index_info.open() if index_info else None

        update_scan = cast(UpdateScan, plan.open())
        count = 0
        while update_scan.next():
            new_value = data.new_value.evaluate(update_scan)
            old_value = update_scan.get_value(target_field)

            update_scan.set_value(target_field, new_value)

            if index:
                record_id = update_scan.get_rid()
                index.delete(old_value, record_id)
                index.insert(new_value, record_id)

            count += 1

        if index:
            index.close()

        update_scan.close()

        return count

    def execute_create_table(self, data: CreateTable, transaction: Transaction) -> int:
        self.metadata_manager.create_table(data.table_name, data.schema, transaction)
        return 0

    def execute_create_view(self, data: CreateView, transaction: Transaction) -> int:
        self.metadata_manager.create_view(data.view_name, data.view_definition(), transaction)
        return 0

    def execute_create_index(self, data: CreateIndex, transaction: Transaction) -> int:
        self.metadata_manager.create_index(data.index_name, data.table_name, data.field_name, transaction)
        return 0
