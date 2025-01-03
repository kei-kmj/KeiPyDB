from abc import ABC
from math import ceil

from db.materialize.temp_table import TempTable
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.layout import Layout
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class MaterializePlan(Plan, ABC):

    def __init__(self, transaction: Transaction, source_plan: Plan) -> None:
        super().__init__()
        self.source_plan = source_plan
        self.transaction = transaction

    def open(self) -> Scan:
        schema = self.source_plan.schema()
        temp_table = TempTable(self.transaction, schema)
        source_scan = self.source_plan.open()
        destination_scan = temp_table.open()

        while source_scan.next():
            destination_scan.insert()
            for field_name in schema.get_fields():
                destination_scan.set_value(field_name, source_scan.get_value(field_name))

        source_scan.close()
        destination_scan.before_first()
        return destination_scan

    def blocks_accessed(self) -> int:

        layout = Layout(self.source_plan.schema())
        records_per_block = self.transaction.block_size() // layout.slot_size

        return ceil(self.source_plan.records_output() / records_per_block)

    def records_output(self) -> int:
        return self.source_plan.records_output()

    def distinct_values(self, field_name: str) -> int:
        return self.source_plan.distinct_values(field_name)

    def schema(self) -> Schema:
        return self.source_plan.schema()
