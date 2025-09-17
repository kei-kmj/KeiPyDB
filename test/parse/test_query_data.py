import pytest

from db.parse.query_data import QueryData
from db.query.predicate import Predicate


class MockPredicate(Predicate):
    def __str__(self):
        return "mock_predicate"


@pytest.fixture
def query_data():
    fields = ["field1", "field2"]
    tables = {"table1", "table2"}
    predicate = MockPredicate()
    return QueryData(fields, tables, predicate)


def test_get_fields(query_data):
    assert query_data.get_fields() == ["field1", "field2"], "フィールドのリストが正しく取得できません"


def test_get_tables(query_data):
    assert query_data.get_tables() == {"table1", "table2"}, "テーブルのリストが正しく取得できません"


def test_get_predicate(query_data):
    assert str(query_data.get_predicate()) == "mock_predicate", "述語が正しく取得できません"


def test_string_representation(query_data):
    # Table order may vary in string representation
    result_str = str(query_data)
    assert "SELECT field1, field2 FROM" in result_str
    assert "WHERE mock_predicate" in result_str
    assert "table1" in result_str and "table2" in result_str
