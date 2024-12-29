import pytest

from db.parse.create_index import CreateIndex


@pytest.fixture
def index_data():
    return CreateIndex(index_name="idx_test", table_name="test_table", field_name="test_field")


def test_インデックス名が取得できること(index_data):
    assert index_data.get_index_name() == "idx_test", "インデックス名が正しく取得できません"


def test_テーブル名が取得できること(index_data):
    assert index_data.get_table_name() == "test_table", "テーブル名が正しく取得できません"


def test_フィールド名が取得できること(index_data):
    assert index_data.get_field_name() == "test_field", "フィールド名が正しく取得できません"
