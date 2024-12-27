import pytest

from db.record.layout import Layout
from db.record.schema import Schema


def test_スキーマから正しいオフセットとスロットサイズが計算されることを確認():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    assert layout.get_offset("test1") == 4
    assert layout.get_offset("test2") == 8
    assert layout.get_offset("test3") == 15
    assert layout.get_slot_size() == 19


def test_既存のオフセットとスロットサイズからLayoutを作成できることを確認する():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    offsets = {"test1": 4, "test2": 8, "test3": 15}
    slot_size = 19

    layout = Layout(schema, offsets, slot_size)

    assert layout.get_offset("test1") == 4
    assert layout.get_offset("test2") == 8
    assert layout.get_offset("test3") == 15
    assert layout.get_slot_size() == 19


def test_存在しないフィールド名で例外が発生することを確認():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    try:
        layout.get_offset("test4")
        assert False
    except KeyError:
        assert True


def test_不明なフィールドタイプに対して例外が発生することを確認する():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    with pytest.raises(KeyError):
        layout._length_in_bytes("test4")
