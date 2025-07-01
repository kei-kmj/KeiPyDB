import pytest

from db.parse.insert_data import InsertData
from db.query.constant import Constant


@pytest.fixture
def table_data():
    return InsertData("table_name", ["id", "name"], [Constant(1), Constant("name")])


def test_get(table_data):

    assert table_data.get_table_name() == "table_name", "テーブル名が正しく取得できません"


def test_field(table_data):

    assert table_data.get_fields() == ["id", "name"], "フィールドが正しく取得できません"
