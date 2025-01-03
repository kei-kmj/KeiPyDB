from typing import Optional

from db.plan.plan import Plan
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.scan import Scan
from db.record.schema import Schema


class Term:

    def __init__(self, left: Expression, right: Expression) -> None:
        self.left = left
        self.right = right

    def is_satisfied(self, scan: Scan) -> bool:

        left_value = self.left.evaluate(scan)
        right_value = self.right.evaluate(scan)

        return left_value == right_value

    def reduction_factor(self, plan: Plan) -> int:
        """クエリの出力レコード数を削減する程度を計算する"""

        if self.left.is_field_name() and self.right.is_field_name():
            left_name = self.left.as_field_name()
            right_name = self.right.as_field_name()

            return max(plan.distinct_values(left_name), plan.distinct_values(right_name))

        if self.left.is_field_name():
            return plan.distinct_values(self.left.as_field_name())

        if self.right.is_field_name():
            return plan.distinct_values(self.right.as_field_name())

        if self.left.as_constant() == self.right.as_constant():
            return 1

        raise ValueError("Reduction factor cannot be determined due to incomparable constants.")

    def equates_with_constant(self, field_name: str) -> Optional[Constant]:
        """TermがF1==F2であることを確認し、フィールドF2を返す"""
        if self.left.is_field_name() and self.left.as_field_name() == field_name and self.right.is_field_name():

            return Constant(self.right.as_field_name())

        elif self.right.is_field_name() and self.right.as_field_name() == field_name and self.left.is_field_name():

            return Constant(self.left.as_field_name())

        return None

    def equates_with_field(self, field_name: str) -> Optional[str]:
        if self.left.is_field_name() and self.left.as_field_name() == field_name and self.right.is_field_name():
            return self.right.as_field_name()
        elif self.right.is_field_name() and self.right.as_field_name() == field_name and self.left.is_field_name():
            return self.left.as_field_name()
        return None

    def applies_to(self, schema: Schema) -> bool:
        """Termがスキーマに適用可能かどうかを返す"""
        return self.left.applies_to(schema) and self.right.applies_to(schema)

    def __str__(self) -> str:
        """Termを文字列で返す"""
        return f"{self.left} = {self.right}"
