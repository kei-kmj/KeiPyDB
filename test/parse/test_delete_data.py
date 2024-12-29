import pytest

from db.parse.delete_data import DeleteData
from db.query.predicate import Predicate


class MockPredicate(Predicate):
    def __str__(self) -> str:
        return "mock_predicate"


@pytest.fixture
def query_data():
    predicate = MockPredicate()
    return DeleteData("table", predicate)


def test_テーブルのリストが取得できること(query_data):
    assert query_data.get_table_name() == "table"


def test_述語が取得できること(query_data):
    assert str(query_data.get_predicate()) == "mock_predicate", "述語が正しく取得できません"
