import pytest

from db.record.schema import Schema


def test_フィールドをスキーマに追加できる():
    schema = Schema()
    schema.add_field("test", 4, 1)

    assert schema.get_fields() == ["test"]
    assert schema.get_type("test") == 4
    assert schema.get_length("test") == 1


def test_整数型のフィールドをスキーマに追加できる():
    schema = Schema()
    schema.add_field("test", 4)

    assert schema.get_type("test") == 4
    assert schema.get_length("test") == 0


def test_文字列フィールドを追加できる():
    schema = Schema()
    schema.add_field("test", 2, 10)

    assert schema.get_type("test") == 2
    assert schema.get_length("test") == 10


def test_他のスキーマに基づいてフィールドを追加できる():
    source_schema = Schema()
    source_schema.add_field("id", 4, 0)
    source_schema.add_field("name", 12, 50)

    target_schema = Schema()
    target_schema.add("id", source_schema)
    target_schema.add("name", source_schema)

    assert target_schema.get_fields() == ["id", "name"]
    assert target_schema.get_type("id") == 4
    assert target_schema.get_type("name") == 12
    assert target_schema.get_length("name") == 50


def test_他のスキーマのすべてのフィールドを追加できる():
    source_schema = Schema()
    source_schema.add_field("id", 4, 0)
    source_schema.add_field("name", 12, 50)

    target_schema = Schema()
    target_schema.add_all(source_schema)

    assert target_schema.get_fields() == ["id", "name"]
    assert target_schema.get_type("id") == 4
    assert target_schema.get_type("name") == 12
    assert target_schema.get_length("name") == 50


def test_指定されたフィールドがスキーマに含まれているかどうかを確認できる():
    schema = Schema()
    schema.add_field("test", 4, 1)

    assert schema.has_field("test") is True
    assert schema.has_field("test2") is False


def test_存在しないフィールドの型を取得しようとするとエラーになる():
    schema = Schema()
    schema.add_field("test", 4, 1)

    with pytest.raises(KeyError):
        schema.get_type("nonexistent_field")

    with pytest.raises(KeyError):
        schema.get_length("nonexistent_field")
