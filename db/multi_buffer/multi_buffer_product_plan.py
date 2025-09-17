from abc import ABC

from db.materialize.materialize_plan import MaterializePlan
from db.materialize.temp_table import TempTable
from db.multi_buffer.multi_buffer_product_scan import MultiBufferProductScan
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class MultiBufferProductPlan(Plan, ABC):

    def __init__(self, transaction: Transaction, left_plan: Plan, right_plan: Plan) -> None:
        super().__init__()
        self.transaction = transaction
        self.left_plan = MaterializePlan(transaction, left_plan)
        self.right_plan = right_plan
        self._schema = Schema()
        self._schema.add_all(self.left_plan.schema())
        self._schema.add_all(self.right_plan.schema())

    def open(self) -> Scan:
        left_scan = self.left_plan.open()
        temp_table = self._copy_records_from(self.right_plan)

        return MultiBufferProductScan(self.transaction, left_scan, temp_table.get_table_name(), temp_table.get_layout())

    def blocks_accessed(self) -> int:
        available_buffers = self.transaction.available_buffers()
        right_materialized_size = MaterializePlan(self.transaction, self.right_plan).blocks_accessed()
        num_chunks = right_materialized_size // available_buffers

        return self.left_plan.blocks_accessed() + right_materialized_size + num_chunks

    def records_output(self) -> int:
        return self.left_plan.records_output() * self.right_plan.records_output()

    def distinct_values(self, field_name: str) -> int:
        if self.left_plan.schema().has_field(field_name):
            return self.left_plan.distinct_values(field_name)
        else:
            return self.right_plan.distinct_values(field_name)

    def schema(self) -> Schema:
        return self._schema

    def _copy_records_from(self, plan: Plan) -> TempTable:

        source_scan = plan.open()
        schema = plan.schema()
        temp_table = TempTable(self.transaction, schema)
        destination_scan = temp_table.open()

        while source_scan.next():
            destination_scan.insert()
            for field_name in schema.get_fields():
                destination_scan.set_value(field_name, source_scan.get_value(field_name))

        source_scan.close()
        destination_scan.close()

        return temp_table
