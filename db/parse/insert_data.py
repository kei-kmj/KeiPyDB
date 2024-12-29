from typing import List

from db.query.constant import Constant


class InsertData:

    def __init__(self, table_name: str, fields: List[str], values: List[Constant]) -> None:
        self.table_name = table_name
        self.fields = fields
        self.values = values

    def get_table_name(self) -> str:
        return self.table_name

    def get_fields(self) -> List[str]:
        return self.fields

    def get_values(self) -> List[Constant]:
        return self.values
