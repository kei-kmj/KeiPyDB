from collections.abc import Collection
from typing import NamedTuple, Optional

from db.query.predicate import Predicate


class OrderByField(NamedTuple):
    field_name: str
    ascending: bool = True

    def __str__(self) -> str:
        return f"{self.field_name} {'ASC' if self.ascending else 'DESC'}"


class QueryData:
    def __init__(
        self,
        fields: list[str],
        tables: Collection[str],
        predicate: Predicate,
        order_by: Optional[list[OrderByField]] = None,
    ) -> None:
        self.fields = fields
        self.tables = tables
        self.predicate = predicate
        self.order_by: list[OrderByField] = list(order_by) if order_by is not None else []

    def get_fields(self) -> list[str]:
        return self.fields

    def get_tables(self) -> Collection[str]:
        return self.tables

    def get_predicate(self) -> Predicate:
        return self.predicate

    def get_order_by(self) -> list[OrderByField]:
        return self.order_by

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

        return query_str
