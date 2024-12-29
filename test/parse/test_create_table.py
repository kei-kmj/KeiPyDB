from db.parse.create_table import CreateTable
from db.record.schema import Schema


def test_テーブル名が取得できる():

    table_data = CreateTable("table_name", Schema())

    assert table_data.get_table_name() == "table_name", "テーブル名が正しく取得できません"


def test_スキーマが取得できる():
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("user_name", 10)
    table_data = CreateTable("table_name", schema)

    assert table_data.get_schema() == schema, "スキーマが正しく取得できません"
