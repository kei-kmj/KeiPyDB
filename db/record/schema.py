from typing import Dict, List

from db.constants import FieldType


class Schema:
    class FieldInfo:
        def __init__(self, field_type: int, length: int):
            self.field_type = field_type
            self.length = length

    def __init__(self) -> None:
        self.fields: List[str] = []
        self.info: Dict[str, Schema.FieldInfo] = {}

    def add_field(self, field_name: str, field_type: int, length: int = 0) -> None:
        """スキーマに名前/型/長さのフィールドを追加"""
        self.fields.append(field_name)
        self.info[field_name] = Schema.FieldInfo(field_type, length)

    def add_int_field(self, field_name: str) -> None:
        """スキーマに整数フィールドを追加"""
        self.add_field(field_name, FieldType.Integer, 0)

    def add_string_field(self, field_name: str, length: int) -> None:
        """スキーマに文字列フィールドを追加"""
        self.add_field(field_name, FieldType.Varchar, length)

    def add(self, field_name: str, schema: "Schema") -> None:
        """別のスキーマに基づいたフィールドをスキーマに追加する"""
        field_type = schema.get_type(field_name)
        field_length = schema.get_length(field_name)
        self.add_field(field_name, field_type, field_length)

    def add_all(self, schema: "Schema") -> None:
        """別のスキーマのすべてのフィールドをスキーマに追加する"""
        for field_name in schema.get_fields():
            self.add(field_name, schema)

    def get_fields(self) -> List[str]:
        """スキーマに含まれるすべてのフィールド名を返す"""
        return self.fields

    def has_field(self, field_name: str) -> bool:
        """スキーマに指定されたフィールドが含まれているかどうかを返す"""
        return field_name in self.fields

    def get_type(self, field_name: str) -> int:
        """指定されたフィールドの型を返す"""
        return self.info[field_name].field_type

    def get_length(self, field_name: str) -> int:
        """指定されたフィールドの長さを返す"""
        return self.info[field_name].length
