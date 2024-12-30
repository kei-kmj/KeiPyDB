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


def test_フィールドのリストが取得できること(query_data):
    assert query_data.get_fields() == ["field1", "field2"], "フィールドのリストが正しく取得できません"


def test_テーブルのリストが取得できること(query_data):
    assert query_data.get_tables() == {"table1", "table2"}, "テーブルのリストが正しく取得できません"


def test_述語が取得できること(query_data):
    assert str(query_data.get_predicate()) == "mock_predicate", "述語が正しく取得できません"


def test_文字列表現が取得できること(query_data):
    assert (
        str(query_data) == "SELECT field1, field2 FROM table2, table1 WHERE mock_predicate"
    ), "文字列表現が正しく取得できません"
