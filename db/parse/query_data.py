from collections.abc import Collection

from db.query.predicate import Predicate


class QueryData:
    def __init__(self, fields: list[str], tables: Collection[str], predicate: Predicate, order_by: list[str] = None) -> None:
        self.fields = fields
        self.tables = tables
        self.predicate = predicate
        self.order_by = order_by or []

    def get_fields(self) -> list[str]:
        return self.fields

    def get_tables(self) -> Collection[str]:
        return self.tables

    def get_predicate(self) -> Predicate:
        return self.predicate

    def get_order_by(self) -> list[str]:
        return self.order_by

    def __str__(self) -> str:

        fields_str = ", ".join(self.fields)
        tables_str = ", ".join(self.tables)
        predicate_str = str(self.predicate)
        order_by_str = ", ".join(self.get_order_by())
        query_str = f"SELECT {fields_str} FROM {tables_str}"

        if predicate_str:
            query_str += f" WHERE {predicate_str}"

        if order_by_str:
            query_str += f" ORDER BY {order_by_str}"

        return query_str
