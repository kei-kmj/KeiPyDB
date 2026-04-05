import pytest

from db.parse.create_index import CreateIndex
from db.parse.create_view import CreateView
from db.parse.delete_data import DeleteData
from db.parse.insert_data import InsertData
from db.parse.modify_data import ModifyData
from db.parse.parser import Parser
from db.parse.query_data import OrderByField, QueryData, VectorOrderBy
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.predicate import Predicate
from db.query.term import Term


def test_parser_select_fields_and_table():
    """フィールドとテーブルのみのSELECT文のパース"""
    sql = "SELECT id, name FROM users"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["id", "name"]
    assert "users" in query_data.get_tables()
    assert query_data.get_predicate() is not None


def test_parser_select_with_where():
    """WHERE句付きSELECT文のパース"""
    sql = "SELECT id, name FROM users WHERE age = 25"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["id", "name"]
    assert "users" in query_data.get_tables()

    predicate = query_data.get_predicate()
    assert predicate is not None


def test_parser_select_with_order_by():
    """ORDER BY句付きSELECT文のパース"""
    sql = "SELECT id, name FROM users ORDER BY name"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    assert query_data.get_order_by() == [OrderByField(field_name="name", ascending=True)]


def test_parser_select_with_order_by_desc():
    """ORDER BY句でDESC指定のSELECT文のパース"""
    sql = "SELECT id, name FROM users ORDER BY name DESC"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    assert query_data.get_order_by() == [OrderByField(field_name="name", ascending=False)]


def test_parser_select_with_multiple_where_conditions():
    """複数条件のSELECT文のパース"""
    sql = "SELECT name FROM users WHERE age = 25 AND status = 'active'"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["name"]
    assert "users" in query_data.get_tables()

    predicate = query_data.get_predicate()
    assert predicate is not None


def test_parser_select_with_limit():
    """LIMIT句付きSELECT文のパース"""
    sql = "SELECT id FROM users LIMIT 10"
    parser = Parser(sql)

    query_data = parser.query()

    assert query_data.get_limit() == 10


def test_parser_select_without_limit():
    """LIMIT句なしのSELECT文のパース"""
    sql = "SELECT id FROM users"
    parser = Parser(sql)

    query_data = parser.query()

    assert query_data.get_limit() is None


def test_parser_insert_fields_and_values():
    """フィールドと値を指定したINSERT文のパース"""
    sql = "INSERT INTO users (id, name, age) VALUES (1, 'John', 25)"
    parser = Parser(sql)

    insert_data = parser.update_command()

    assert isinstance(insert_data, InsertData)
    assert insert_data.get_table_name() == "users"
    assert insert_data.get_fields() == ["id", "name", "age"]

    values = insert_data.get_values()
    assert len(values) == 3
    assert isinstance(values[0], Constant)
    assert isinstance(values[1], Constant)
    assert isinstance(values[2], Constant)


def test_parser_insert_with_different_types():
    """異なるデータ型のINSERT文のパース"""
    sql = "INSERT INTO products (id, name, price, description) VALUES (100, 'Widget', 1500, 'A useful widget')"
    parser = Parser(sql)

    insert_data = parser.update_command()

    assert isinstance(insert_data, InsertData)
    assert insert_data.get_table_name() == "products"
    assert len(insert_data.get_fields()) == 4
    assert len(insert_data.get_values()) == 4


def test_parser_delete_without_where():
    """WHERE句なしのDELETE文のパース"""
    sql = "DELETE FROM users"
    parser = Parser(sql)

    delete_data = parser.update_command()

    assert isinstance(delete_data, DeleteData)
    assert delete_data.get_table_name() == "users"

    predicate = delete_data.get_predicate()
    assert predicate is not None  # 空の述語オブジェクト


def test_parser_delete_with_where():
    """WHERE句付きのDELETE文のパース"""
    sql = "DELETE FROM users WHERE age = 65"
    parser = Parser(sql)

    delete_data = parser.update_command()

    assert isinstance(delete_data, DeleteData)
    assert delete_data.get_table_name() == "users"

    predicate = delete_data.get_predicate()
    assert predicate is not None


def test_parser_update_with_where():
    """WHERE句付きUPDATE文のパース"""
    sql = "UPDATE users SET age = 26 WHERE id = 1"
    parser = Parser(sql)

    modify_data = parser.update_command()

    assert isinstance(modify_data, ModifyData)
    assert modify_data.get_table_name() == "users"
    assert modify_data.get_field_name() == "age"

    new_value = modify_data.get_new_value()
    assert isinstance(new_value, Expression)

    predicate = modify_data.get_predicate()
    assert predicate is not None


def test_parser_update_with_string():
    """文字列値のUPDATE文のパース"""
    sql = "UPDATE users SET name = 'Updated Name' WHERE id = 1"
    parser = Parser(sql)

    modify_data = parser.update_command()

    assert isinstance(modify_data, ModifyData)
    assert modify_data.get_table_name() == "users"
    assert modify_data.get_field_name() == "name"


def test_parser_create_view():
    """CREATE VIEW文のパース"""
    sql = "CREATE VIEW active_users AS SELECT id, name FROM users WHERE status = 'active'"
    parser = Parser(sql)

    create_view = parser.update_command()

    assert isinstance(create_view, CreateView)
    assert create_view.get_view_name() == "active_users"

    view_def = create_view.view_definition()
    assert "SELECT" in view_def
    assert "FROM users" in view_def
    assert "WHERE" in view_def


def test_parser_create_index():
    """CREATE INDEX文のパース"""
    sql = "CREATE INDEX idx_users_name ON users (name)"
    parser = Parser(sql)

    create_index = parser.update_command()

    assert isinstance(create_index, CreateIndex)
    assert create_index.get_index_name() == "idx_users_name"
    assert create_index.get_table_name() == "users"
    assert create_index.get_field_name() == "name"


def test_parser_field_parsing():
    """フィールドパースのテスト"""
    sql = "SELECT id FROM users"
    parser = Parser(sql)

    # fieldsの部分をテスト
    parser.lexer.eat_keyword("SELECT")
    field = parser.field()

    assert field == "id"


def test_parser_constant_parsing_int():
    """整数定数パースのテスト"""
    sql = "SELECT 123 FROM users"
    parser = Parser(sql)

    parser.lexer.eat_keyword("SELECT")
    constant = parser.constant()

    assert isinstance(constant, Constant)
    assert constant.as_int() == 123


def test_parser_constant_parsing_string():
    """文字列定数パースのテスト"""
    sql = "SELECT 'hello' FROM users"
    parser = Parser(sql)

    parser.lexer.eat_keyword("SELECT")
    constant = parser.constant()

    assert isinstance(constant, Constant)
    assert isinstance(constant.as_string(), str)


def test_parser_expression_field():
    """フィールド式のパースのテスト"""
    sql = "SELECT name FROM users"
    parser = Parser(sql)

    parser.lexer.eat_keyword("SELECT")
    expression = parser.expression()

    assert isinstance(expression, Expression)
    assert expression.is_field_name()
    assert expression.as_field_name() == "name"


def test_parser_expression_constant():
    """定数式のパースのテスト"""
    sql = "SELECT 42 FROM users"
    parser = Parser(sql)

    parser.lexer.eat_keyword("SELECT")
    expression = parser.expression()

    assert isinstance(expression, Expression)
    # Expression doesn't have is_constant method
    assert expression.as_constant() is not None


def test_parser_term_parsing():
    """項のパースのテスト"""
    sql = "SELECT * FROM users WHERE age = 25"
    parser = Parser(sql)

    # WHERE句まで進む
    parser.lexer.eat_keyword("SELECT")
    parser.lexer.eat_delimiter("*")
    parser.lexer.eat_keyword("FROM")
    parser.lexer.eat_id()  # users
    parser.lexer.eat_keyword("WHERE")

    term = parser.term()

    assert isinstance(term, Term)


def test_parser_predicate_parsing():
    """述語のパースのテスト"""
    sql = "SELECT * FROM users WHERE age = 25 AND status = 'active'"
    parser = Parser(sql)

    # WHERE句まで進む
    parser.lexer.eat_keyword("SELECT")
    parser.lexer.eat_delimiter("*")
    parser.lexer.eat_keyword("FROM")
    parser.lexer.eat_id()  # users
    parser.lexer.eat_keyword("WHERE")

    predicate = parser.predicate()

    assert isinstance(predicate, Predicate)


def test_parser_syntax_error_invalid_keyword():
    """無効なキーワードでの構文エラーテスト"""
    sql = "INVALID COMMAND"
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.query()


def test_parser_syntax_error_incomplete_select():
    """不完全なSELECT文での構文エラーテスト"""
    sql = "SELECT id FROM"  # テーブル名がない
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.query()


def test_parser_syntax_error_incomplete_insert():
    """不完全なINSERT文での構文エラーテスト"""
    sql = "INSERT INTO users (id) VALUES"  # 値がない
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.update_command()


def test_parser_syntax_error_invalid_create():
    """無効なCREATE文での構文エラーテスト"""
    sql = "CREATE INVALID STATEMENT"
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.update_command()


def test_parser_edge_case_empty_string():
    """空文字列での構文エラーテスト"""
    sql = ""
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.query()


def test_parser_edge_case_only_whitespace():
    """空白のみでの構文エラーテスト"""
    sql = "   \t\n   "
    parser = Parser(sql)

    with pytest.raises(SyntaxError):
        parser.query()


def test_query_with_vector_order_by():
    """ベクトルソートのクエリのパーステスト"""
    sql = "SELECT id FROM items ORDER BY embedding <-> '[1.0, 2.0, 3.0]'"
    parser = Parser(sql)

    query_data = parser.query()

    assert isinstance(query_data, QueryData)
    order_by = query_data.get_order_by()
    assert len(order_by) == 1
    assert isinstance(order_by[0], VectorOrderBy)
    assert order_by[0].field_name == "embedding"
    assert order_by[0].query_vector == [1.0, 2.0, 3.0]
