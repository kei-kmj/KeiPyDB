from db.query.constant import Constant
from db.query.scan import Scan
from db.record.schema import Schema


class Expression:
    def __init__(self, value: Constant, field_name: str) -> None:
        self.value = value
        self.field_name = field_name

    def evaluate(self, scan: Scan) -> int | str | Constant:
        """現在のスキャンに基づいて式を評価する"""
        return self.value if self.value is not None else scan.get_val(self.field_name)

    def is_field_name(self) -> bool:
        """式がフィールド名かどうかを返す"""
        return self.field_name is not None

    def as_constant(self) -> Constant:
        """式を定数として返す"""
        return self.value

    def as_field_name(self) -> str:
        """式をフィールド名として返す"""
        return self.field_name

    def applies_to(self, schema: Schema) -> bool:
        """式がスキーマに適用可能かどうかを返す"""
        return True if self.value is not None else schema.has_field(self.field_name)

    def __str__(self) -> str:
        """式を文字列で返す"""
        return str(self.value) if self.value is not None else self.field_name
