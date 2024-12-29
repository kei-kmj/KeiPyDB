from collections.abc import Collection
from typing import List

from db.query.predicate import Predicate


class QueryData:
    def __init__(self, fields: List[str], tables: Collection[str], predicate: Predicate) -> None:
        self.fields = fields
        self.tables = tables
        self.predicate = predicate

    def get_fields(self) -> List[str]:
        return self.fields

    def get_tables(self) -> Collection[str]:
        return self.tables

    def get_predicate(self) -> Predicate:
        return self.predicate

    def __str__(self) -> str:

        fields_str = ", ".join(self.fields)
        tables_str = ", ".join(self.tables)
        predicate_str = str(self.predicate)
        query_str = f"SELECT {fields_str} FROM {tables_str}"

        if predicate_str:
            query_str += f" WHERE {predicate_str}"

        return query_str
