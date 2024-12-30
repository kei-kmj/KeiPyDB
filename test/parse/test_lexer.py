from db.parse.lexer import Lexer


def test_デリミタが一致することを確認する():
    sql = "SELECT * FROM table;"
    lexer = Lexer(sql)

    assert lexer.match_delimiter("SELECT") is True
    lexer.next_token()
    assert lexer.match_delimiter("*") is True
    lexer.next_token()
    assert lexer.match_delimiter("FROM") is True


def test_整数定数が一致することを確認する():
    sql = "SELECT 123 FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.match_int_constant() is True


def test_文字列定数が一致することを確認する():
    sql = "SELECT 'value' FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.match_string_constant() is True


def test_識別子が一致することを確認する():
    sql = "SELECT Column_name FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    print("lexer★", vars(lexer))
    assert lexer.match_id() is True


def test_整数定数を消費できることを確認する():
    sql = "SELECT 123 FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_int_constant() == 123


def test_文字列定数を消費できることを確認する():
    sql = "SELECT 'value' FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_string_constant() == "'value'"


def test_識別子を消費できることを確認する():
    sql = "SELECT Column_name FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_id() == "column_name"


def test_キーワードを消費できることを確認する():
    sql = "SELECT * FROM table;"
    lexer = Lexer(sql)

    lexer.eat_keyword("SELECT")
    assert lexer.current_token == "*"
    lexer.eat_keyword("*")
    assert lexer.current_token == "from"
    lexer.eat_keyword("FROM")
    assert lexer.current_token == "table"
    lexer.eat_keyword("table")
    assert lexer.current_token == ";"
    lexer.eat_delimiter(";")
    assert lexer.current_token is None
