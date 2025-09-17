from db.record.schema import Schema


class CreateTable:
    def __init__(self, table_name: str, schema: Schema):
        self.table_name = table_name
        self.schema = schema

    def get_table_name(self) -> str:
        return self.table_name

    def get_schema(self) -> Schema:
        return self.schema
