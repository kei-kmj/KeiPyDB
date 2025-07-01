import pytest

from db.constants import FieldType
from db.parse.bad_syntax_exception import BadSyntaxException
from db.parse.parser import Parser
from db.parse.query_data import QueryData
from db.parse.insert_data import InsertData
from db.parse.delete_data import DeleteData
from db.parse.modify_data import ModifyData
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.create_index import CreateIndex
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.predicate import Predicate
from db.query.term import Term


def test_parser_select_basic():
    """基本的なSELECT文のパース"""
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
    # 述語の詳細確認（実装依存）


@pytest.mark.skip
def test_parser_select_multiple_tables():
    """複数テーブルのSELECT文のパース"""
    sql = "SELECT u.name, p.title FROM users u, products p WHERE u.id = p.user_id"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    # テーブルエイリアスの処理確認
    tables = query_data.get_tables()
    assert len(tables) >= 2


def test_parser_select_and_condition():
    """複数条件のSELECT文のパース"""
    sql = "SELECT name FROM users WHERE age = 25 AND status = 'active'"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["name"]
    assert "users" in query_data.get_tables()
    
    predicate = query_data.get_predicate()
    assert predicate is not None


def test_parser_insert_basic():
    """基本的なINSERT文のパース"""
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


@pytest.mark.skip
def test_parser_delete_with_where():
    """WHERE句付きのDELETE文のパース"""
    sql = "DELETE FROM users WHERE age > 65"
    parser = Parser(sql)
    
    delete_data = parser.update_command()
    
    assert isinstance(delete_data, DeleteData)
    assert delete_data.get_table_name() == "users"
    
    predicate = delete_data.get_predicate()
    assert predicate is not None


def test_parser_update_basic():
    """基本的なUPDATE文のパース"""
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


@pytest.mark.skip
def test_parser_create_table_basic():
    """基本的なCREATE TABLE文のパース"""
    sql = "CREATE TABLE users (id int, name varchar(50), age int)"
    parser = Parser(sql)
    
    create_table = parser.update_command()
    
    assert isinstance(create_table, CreateTable)
    assert create_table.get_table_name() == "users"
    
    schema = create_table.get_schema()
    assert schema is not None
    assert schema.has_field("id")
    assert schema.has_field("name")
    assert schema.has_field("age")
    
    # フィールドタイプの確認
    assert schema.type("id") == FieldType.Integer
    assert schema.type("name") == FieldType.Varchar
    assert schema.type("age") == FieldType.Integer
    
    # varchar長の確認
    assert schema.length("name") == 50


def test_parser_create_table_complex():
    """複雑なCREATE TABLE文のパース"""
    sql = "CREATE TABLE products (product_id int, title varchar(100), description varchar(500), price int, category varchar(30))"
    parser = Parser(sql)
    
    create_table = parser.update_command()
    
    assert isinstance(create_table, CreateTable)
    assert create_table.get_table_name() == "products"
    
    schema = create_table.get_schema()
    assert len(schema.fields) == 5
    
    # 各フィールドの確認
    expected_fields = ["product_id", "title", "description", "price", "category"]
    for field in expected_fields:
        assert schema.has_field(field)


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
    field = parser.filed()
    
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


@pytest.mark.skip
def test_parser_expression_constant():
    """定数式のパースのテスト"""
    sql = "SELECT 42 FROM users"
    parser = Parser(sql)
    
    parser.lexer.eat_keyword("SELECT")
    expression = parser.expression()
    
    assert isinstance(expression, Expression)
    assert expression.is_constant()


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


@pytest.mark.skip
def test_parser_syntax_error_invalid_keyword():
    """無効なキーワードでの構文エラーテスト"""
    sql = "INVALID COMMAND"
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.query()


@pytest.mark.skip
def test_parser_syntax_error_incomplete_select():
    """不完全なSELECT文での構文エラーテスト"""
    sql = "SELECT id FROM"  # テーブル名がない
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.query()


@pytest.mark.skip
def test_parser_syntax_error_incomplete_insert():
    """不完全なINSERT文での構文エラーテスト"""
    sql = "INSERT INTO users (id) VALUES"  # 値がない
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.update_command()

@pytest.mark.skip
def test_parser_syntax_error_invalid_create():
    """無効なCREATE文での構文エラーテスト"""
    sql = "CREATE INVALID STATEMENT"
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.update_command()


@pytest.mark.skip
def test_parser_edge_case_empty_string():
    """空文字列での構文エラーテスト"""
    sql = ""
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.query()

@pytest.mark.skip
def test_parser_edge_case_only_whitespace():
    """空白のみでの構文エラーテスト"""
    sql = "   \t\n   "
    parser = Parser(sql)
    
    with pytest.raises(BadSyntaxException):
        parser.query()


def test_parser_case_insensitive_keywords():
    """キーワードの大文字小文字無関係のテスト"""
    sql = "select id, name from users where age = 25"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["id", "name"]
    assert "users" in query_data.get_tables()


def test_parser_mixed_case_keywords():
    """混在する大文字小文字のテスト"""
    sql = "Select Id, Name From Users Where Age = 25"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    assert query_data.get_fields() == ["id", "name"]  # 小文字に正規化される


def test_parser_complex_where_clause():
    """複雑なWHERE句のテスト"""
    sql = "SELECT name FROM users WHERE age = 25 AND status = 'active' AND department = 'IT'"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    predicate = query_data.get_predicate()
    assert predicate is not None


def test_parser_multiple_field_select():
    """多数フィールドのSELECT文のテスト"""
    sql = "SELECT id, name, email, age, department, salary, hire_date FROM employees"
    parser = Parser(sql)
    
    query_data = parser.query()
    
    assert isinstance(query_data, QueryData)
    fields = query_data.get_fields()
    assert len(fields) == 7
    expected_fields = ["id", "name", "email", "age", "department", "salary", "hire_date"]
    assert fields == expected_fields


@pytest.mark.skip
def test_parser_create_table_various_types():
    """様々なデータ型のCREATE TABLEテスト"""
    sql = "CREATE TABLE test_table (small_int int, medium_text varchar(100), large_text varchar(500), another_int int)"
    parser = Parser(sql)
    
    create_table = parser.update_command()
    
    assert isinstance(create_table, CreateTable)
    schema = create_table.get_schema()
    
    assert schema.type("small_int") == FieldType.Integer
    assert schema.type("medium_text") == FieldType.Varchar
    assert schema.type("large_text") == FieldType.Varchar
    assert schema.type("another_int") == FieldType.Integer
    
    assert schema.length("medium_text") == 100
    assert schema.length("large_text") == 500


def test_parser_stress_test_large_insert():
    """大きなINSERT文のストレステスト"""
    fields = [f"field_{i}" for i in range(20)]
    values = [f"'value_{i}'" if i % 2 == 0 else str(i) for i in range(20)]
    
    sql = f"INSERT INTO large_table ({', '.join(fields)}) VALUES ({', '.join(values)})"
    parser = Parser(sql)
    
    insert_data = parser.update_command()
    
    assert isinstance(insert_data, InsertData)
    assert len(insert_data.get_fields()) == 20
    assert len(insert_data.get_values()) == 20