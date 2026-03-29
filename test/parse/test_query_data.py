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


def test_get_order_by(query_data):
    fields = ["field1"]
    tables = {"table1"}
    predicate = Predicate()
    query_data = QueryData(fields, tables, predicate, order_by=["field1"])
    assert query_data.get_order_by() == ["field1"]

def test_get_order_by_default_empty():
    fields = ["field1"]
    tables = {"table1"}
    predicate = Predicate()
    query_data = QueryData(fields, tables, predicate)
    assert query_data.get_order_by() == []

def test_string_representation_with_order_by(query_data):
    # Table order may vary in string representation
    fields = ["field1", "field2"]
    tables = {"table1"}
    predicate = Predicate()
    query_data = QueryData(fields, tables, predicate, order_by=["field1", "field2"])
    result_str = str(query_data)
    assert "ORDER BY field1, field2" in result_str


def test_string_representation_without_order_by(query_data):
    assert "ORDER BY" not in str(query_data)
