import pytest

from db.parse.insert_data import InsertData
from db.query.constant import Constant


@pytest.fixture
def table_data():
    return InsertData("table_name", ["id", "name"], [Constant(1), Constant("name")])


def test_テーブル名が取得できる(table_data):

    assert table_data.get_table_name() == "table_name", "テーブル名が正しく取得できません"


def test_フィールドが取得できる(table_data):

    assert table_data.get_fields() == ["id", "name"], "フィールドが正しく取得できません"


def test_値が取得できる(table_data):

    assert table_data.get_values() == [Constant(1), Constant("name")], "値が正しく取得できません"
