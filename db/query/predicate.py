from typing import Optional

from db.plan.plan import Plan
from db.query.constant import Constant
from db.query.scan import Scan
from db.query.term import Term
from db.record.schema import Schema


class Predicate:
    def __init__(self, terms: Optional[list[Term]] = None):
        self.terms = terms if terms else []

    def add_term(self, term: Term) -> None:
        """単一のTermを追加"""
        self.terms.append(term)

    def conjoin_with(self, other: "Predicate") -> None:
        """自信と指定された述語の論理積を取る"""
        self.terms.extend(other.terms)

    def is_satisfied(self, scan: Scan) -> bool:
        """指定されたスキャンに述語が適用されるかどうかを返す"""
        return all(term.is_satisfied(scan) for term in self.terms)

    def reduction_factor(self, plan: Plan) -> int:
        """クエリの出力レコード数を削減する程度を計算する"""
        factor = 1
        for term in self.terms:
            factor *= term.reduction_factor(plan)
        return factor

    def select_sub_predicate(self, schema: Schema) -> Optional["Predicate"]:
        """指定されたスキーマに適用される部分熟語を返す"""
        applicable_terms = [term for term in self.terms if term.applies_to(schema)]
        return Predicate(applicable_terms) if applicable_terms else None

    def join_sub_predicate(self, schema1: Schema, schema2: Schema) -> Optional["Predicate"]:
        """指定されたスキーマに適用される部分熟語を返す"""
        joined_schema = Schema()
        joined_schema.add_all(schema1)
        joined_schema.add_all(schema2)

        application_terms = [
            term
            for term in self.terms
            if not term.applies_to(schema1) and not term.applies_to(schema2) and term.applies_to(joined_schema)
        ]
        return Predicate(application_terms) if application_terms else None

    def equates_with_constant(self, field_name: str) -> Optional[Constant]:
        """指定されたフィールド名が定数と等しい場合、フィールド名を返す"""
        for term in self.terms:
            constant = term.equates_with_constant(field_name)
            if constant is not None:
                return constant
        return None

    def equates_with_field(self, field_name: str) -> Optional[str]:
        for term in self.terms:
            result = term.equates_with_field(field_name)
            if result is not None:
                return result
        return None

    def __str__(self) -> str:
        """述語を文字列で返す"""
        return " and ".join(str(term) for term in self.terms)
