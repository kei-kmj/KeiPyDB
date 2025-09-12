from db.query.constant import Constant


class InsertData:

    def __init__(self, table_name: str, fields: list[str], values: list[Constant]) -> None:
        self.table_name = table_name
        self.fields = fields
        self.values = values

    def get_table_name(self) -> str:
        return self.table_name

    def get_fields(self) -> list[str]:
        return self.fields

    def get_values(self) -> list[Constant]:
        return self.values
