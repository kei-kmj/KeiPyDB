from unittest.mock import Mock

from db.query.constant import Constant
from db.query.expression import Expression



# def test_定数式の評価ができる():
#     constant = Constant()
#
#     expression = Expression(constant, "")
#     mock_scan = Mock()
#     result = expression.evaluate(mock_scan)
#
#     assert result == constant
#
# def test_フィールド式の評価ができる():
#     field_name = "field1"
#     constant = Constant()
#     mock_scan = Mock()
#     mock_scan.constant = constant
#     expression = Expression(constant, field_name)
#     result = expression.evaluate(mock_scan)
#
#     assert result == mock_scan.constant