from db.query.constant import Constant


def test_整数値の定数を初期化できる():
    constant = Constant(1)
    assert constant.value == 1


def test_文字列値の定数を初期化できる():
    constant = Constant("value")
    assert constant.value == "value"


def test_不正な型の定数を初期化するとエラーになる():
    try:
        Constant(1.0)
        assert False
    except ValueError:
        assert True

def test_等価な整数値の定数を比較できる():
    constant = Constant(1)
    other_constant = Constant(1)
    assert constant == other_constant

def test_異なる値の定数が等しくないと判断される():
    constant = Constant(1)
    other_constant = Constant(2)
    assert constant != other_constant


def test_定数のハッシュ値が値に基づいて生成される():
    constant = Constant(1)
    assert hash(constant) == hash(1)


def test_整数型の定数を文字列に変換できる():
    constant = Constant(1)
    assert str(constant) == "1"


def test_文字列型の定数を文字列に変換できる():
    constant = Constant("value")
    assert str(constant) == "value"

def test_整数としての定数を正しく返す():
    constant = Constant(1)
    assert constant.as_int() == 1

def test_整数ではない定数を整数に変換するとエラーになる():
    constant = Constant("value")
    try:
        constant.as_int()
        assert False
    except ValueError:
        assert True

def test_文字列としての定数を正しく返す():
    constant = Constant("value")
    assert constant.as_string() == "value"

def test_文字列ではない定数を文字列に変換するとエラーになる():
    constant = Constant(1)
    try:
        constant.as_string()
        assert False
    except ValueError:
        assert True