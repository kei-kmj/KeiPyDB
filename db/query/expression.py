from typing import Optional, Union

from db.query.constant import Constant
from db.query.scan import Scan
from db.record.schema import Schema


class Expression:
    def __init__(self, literal_or_field: Union[Constant, str]) -> None:

        if isinstance(literal_or_field, Constant):
            self.constant: Optional[Constant] = literal_or_field
            self.field_name: Optional[str] = None

        elif isinstance(literal_or_field, str):
            self.constant = None
            self.field_name = literal_or_field
        else:
            raise ValueError("Invalid argument: must be a Constant or a string")

    def evaluate(self, scan: Scan) -> Constant:
        """現在のスキャンに基づいて式を評価する"""
        if not self.field_name or not self.constant:
            raise ValueError("Expression is not a field name or a constant.")

        if self.constant is not None:
            return self.constant
        elif self.field_name is not None:
            return scan.get_val(self.field_name)

    def is_field_name(self) -> bool:
        """式がフィールド名かどうかを返す"""
        return self.field_name is not None

    def as_constant(self) -> Constant:
        """式を定数として返す"""
        if not self.constant:
            raise ValueError("Expression is not a constant.")

        return self.constant

    def as_field_name(self) -> str:
        """式をフィールド名として返す"""
        if self.field_name is None:
            raise ValueError("Expression is not a field name.")
        return self.field_name

    def applies_to(self, schema: Schema) -> bool:
        """式がスキーマに適用可能かどうかを返す"""
        if self.field_name is not None:
            return schema.has_field(self.field_name)
        return True

    def __str__(self) -> str:
        """式を文字列で返す"""
        if self.field_name is not None:
            return self.field_name
        elif self.constant is not None:
            return str(self.constant)
        return "<invalid expression>"
