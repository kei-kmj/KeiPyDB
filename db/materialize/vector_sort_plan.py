from abc import ABC
from typing import Optional, cast

from db.constants import FieldType
from db.index.vector_index import VectorIndex
from db.materialize.temp_table import TempTable
from db.parse.query_data import VectorOrderBy
from db.plan.plan import Plan
from db.query.constant import Constant
from db.query.scan import Scan
from db.query.vector import Vector, cosine_distance
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction

type VectorSearchResult = tuple[float, dict[str, Constant | Vector]]


class VectorSortPlan(Plan, ABC):
    def __init__(
        self,
        transaction: Transaction,
        plan: Plan,
        vector_order_by: VectorOrderBy,
        vector_index: Optional[VectorIndex] = None,
    ) -> None:
        super().__init__()
        self.transaction = transaction
        self.plan = plan
        self.vector_order_by = vector_order_by
        self.vector_index = vector_index

    def open(self) -> Scan:
        schema = self.plan.schema()
        field_name = self.vector_order_by.field_name
        query_vector = self.vector_order_by.query_vector

        if self.vector_index is not None:
            rows = self._search_by_index(schema, field_name, query_vector)
        else:
            rows = self._search_by_linear(schema, field_name, query_vector)

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

    def _search_by_linear(self, schema: Schema, field_name: str, query_vector: list[float]) -> list[VectorSearchResult]:

        source_scan = self.plan.open()
        rows: list[VectorSearchResult] = []

        while source_scan.next():
            row: dict[str, Constant | Vector] = {}
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
        return rows

    def _search_by_index(self, schema: Schema, field_name: str, query_vector: Vector) -> list[VectorSearchResult]:

        if self.vector_index is None:
            raise RuntimeError("Vector index is not provided for index-based search")

        k = self.vector_index.default_k
        records_ids = self.vector_index.search(query_vector, k=k)
        source_scan = self.plan.open()
        table_scan = cast(TableScan, source_scan)

        rows: list[VectorSearchResult] = []
        for record_id in records_ids:
            table_scan.move_to_rid(record_id)
            row: dict[str, Constant | Vector] = {}
            for f in schema.get_fields():
                if schema.get_type(f) == FieldType.Vector:
                    row[f] = table_scan.get_vector(f)
                else:
                    row[f] = table_scan.get_value(f)

            vector = table_scan.get_vector(field_name)
            distance = cosine_distance(vector, query_vector)
            rows.append((distance, row))

        table_scan.close()
        return rows
