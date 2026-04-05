from abc import ABC

from db.constants import FieldType
from db.materialize.temp_table import TempTable
from db.parse.query_data import VectorOrderBy
from db.plan.plan import Plan
from db.query.constant import Constant
from db.query.scan import Scan
from db.query.vector import cosine_distance
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class VectorSortPlan(Plan, ABC):
    def __init__(self, transaction: Transaction, plan: Plan, vector_order_by: VectorOrderBy) -> None:
        super().__init__()
        self.transaction = transaction
        self.plan = plan
        self.vector_order_by = vector_order_by

    def open(self) -> Scan:
        source_scan = self.plan.open()
        schema = self.plan.schema()
        field_name = self.vector_order_by.field_name
        query_vector = self.vector_order_by.query_vector

        rows = []
        while source_scan.next():
            row: dict[str, Constant | list[float]] = {}
            for f in schema.get_fields():
                if schema.get_type(f) == FieldType.Vector:
                    row[f] = source_scan.get_vector(f)
                else:
                    row[f] = source_scan.get_value(f)

            vector = source_scan.get_vector(field_name)
            distance = cosine_distance(vector, query_vector)
            rows.append((distance, row))

        source_scan.close()
        rows.sort(key=lambda x: x[0])

        temp = TempTable(self.transaction, schema)
        destination_scan = temp.open()
        for _, row in rows:
            destination_scan.insert()
            for f in schema.get_fields():
                value = row[f]
                if isinstance(value, list):
                    destination_scan.set_vector(f, value)
                else:
                    destination_scan.set_value(f, value)
        destination_scan.before_first()

        return destination_scan

    def schema(self) -> Schema:
        return self.plan.schema()

    def distinct_values(self, field_name: str) -> int:
        return self.plan.distinct_values(field_name)

    def records_output(self) -> int:
        return self.plan.records_output()

    def blocks_accessed(self) -> int:
        return self.plan.blocks_accessed()
