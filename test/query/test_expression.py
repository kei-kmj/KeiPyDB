from unittest.mock import Mock

import pytest

from db.query.constant import Constant
from db.query.expression import Expression


@pytest.mark.skip(reason="TODO:後で見直す")
def test_定数式の評価ができる():
    constant = Constant(42)
    expression = Expression(constant)

    result = expression.evaluate(scan=Mock())

    assert result == constant, "定数式の評価が正しくありません"


@pytest.mark.skip(reason="TODO:後で見直す")
def test_フィールド式の評価ができる():
    field_name = "field_name"
    scan = Mock()
    scan.get_val.return_value = Constant(42)
    expression = Expression(field_name)

    result = expression.evaluate(scan)

    assert result == Constant(42), "フィールド式の評価が正しくありません"


def test_フィールド名判定が正しい():
    field_name = "field_name"
    expression = Expression(field_name)

    result = expression.is_field_name()

    assert result is True, "フィールド名判定が正しくありません"



def test_フィールド名を取得できる():
    field_name = "field_name"
    expression = Expression(field_name)

    result = expression.as_field_name()

    assert result == field_name, "フィールド名を取得できません"


def test_スキーマに適用可能かを判定できる():
    field_name = "field_name"
    schema = Mock()
    schema.has_field.return_value = True
    expression = Expression(field_name)

    result = expression.applies_to(schema)

    assert result is True, "スキーマに適用可能かを判定できません"
