from db.parse.lexer import Lexer


def test_delimiter_matches_correctly():
    sql = "SELECT * FROM table;"
    lexer = Lexer(sql)

    assert lexer.match_delimiter("SELECT") is True
    lexer.next_token()
    assert lexer.match_delimiter("*") is True
    lexer.next_token()
    assert lexer.match_delimiter("FROM") is True


def test_integer_constant_matches_correctly():
    sql = "SELECT 123 FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.match_int_constant() is True


def test_string_constant_matches_correctly():
    sql = "SELECT 'value' FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.match_string_constant() is True


def test_identifier_matches_correctly():
    sql = "SELECT Column_name FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.match_id() is True


def test_can_consume_integer_constant():
    sql = "SELECT 123 FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_int_constant() == 123


def test_can_consume_string_constant():
    sql = "SELECT 'value' FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_string_constant() == "'value'"


def test_can_consume_identifier():
    sql = "SELECT Column_name FROM table;"
    lexer = Lexer(sql)

    lexer.next_token()
    assert lexer.eat_id() == "column_name"


def test_can_consume_keyword():
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
