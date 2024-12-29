from unittest.mock import Mock

import pytest

from db.parse.modify_data import ModifyData
from db.query.expression import Expression


@pytest.fixture
def modify_data():
    table_name = "test_table"
    field_name = "test_field"
    new_value = Mock(spec=Expression)
    predicate = Mock(spec=Expression)
    return ModifyData(table_name, field_name, new_value, predicate)


def test_テーブル名が取得できること(modify_data):
    assert modify_data.get_table_name() == "test_table", "テーブル名が正しく取得できません"


def test_フィールド名を取得できる(modify_data):
    assert modify_data.get_field_name() == "test_field", "フィールド名が正しく取得できません"


def test_新しい値を取得できる(modify_data):
    assert modify_data.get_new_value() == modify_data.new_value, "新しい値が正しく取得できません"


def test_条件式を取得できる(modify_data):
    assert modify_data.get_predicate() == modify_data.predicate, "条件式が正しく取得できません"
