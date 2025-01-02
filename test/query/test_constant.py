from db.query.constant import Constant


def test_整数値の定数を初期化できる():
    constant = Constant(1)
    assert constant.int_value == 1


def test_文字列の定数を初期化できる():
    constant = Constant("test")
    assert constant.str_value == "test"


def test_定数の型を取得できる():
    constant = Constant(1)
    assert constant.as_int() == 1


