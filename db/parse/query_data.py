from collections.abc import Collection
from typing import NamedTuple, Optional

from db.query.predicate import Predicate


class OrderByField(NamedTuple):
    field_name: str
    ascending: bool = True

    def __str__(self) -> str:
        return f"{self.field_name} {'ASC' if self.ascending else 'DESC'}"


class VectorOrderBy(NamedTuple):
    field_name: str
    query_vector: list[float]

    def __str__(self) -> str:
        vector_str = "[" + ", ".join(str(v) for v in self.query_vector) + "]"
        return f"{self.field_name} <-> '{vector_str}'"


class QueryData:
    def __init__(
        self,
        fields: list[str],
        tables: Collection[str],
        predicate: Predicate,
        order_by: Optional[list[OrderByField | VectorOrderBy]] = None,
        limit: Optional[int] = None,
    ) -> None:
        self.fields = fields
        self.tables = tables
        self.predicate = predicate
        self.order_by: list[OrderByField | VectorOrderBy] = list(order_by) if order_by is not None else []
        self.limit = limit

    def get_fields(self) -> list[str]:
        return self.fields

    def get_tables(self) -> Collection[str]:
        return self.tables

    def get_predicate(self) -> Predicate:
        return self.predicate

    def get_order_by(self) -> list[OrderByField | VectorOrderBy]:
        return self.order_by

    def get_limit(self) -> Optional[int]:
        return self.limit

    def __str__(self) -> str:

        fields_str = ", ".join(self.fields)
        tables_str = ", ".join(self.tables)
        predicate_str = str(self.predicate)
        order_by_str = ", ".join(str(f) for f in self.get_order_by())
        query_str = f"SELECT {fields_str} FROM {tables_str}"

        if predicate_str:
            query_str += f" WHERE {predicate_str}"

        if order_by_str:
            query_str += f" ORDER BY {order_by_str}"

        if self.limit is not None:
            query_str += f" LIMIT {self.limit}"

        return query_str
