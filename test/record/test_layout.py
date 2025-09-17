import pytest

from db.constants import ByteSize, FieldType
from db.file.page import Page
from db.record.layout import Layout
from db.record.schema import Schema


def test_correct_offsets_and_slot_size_calculated_from_schema():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    assert layout.get_offset("test1") == 4
    assert layout.get_offset("test2") == 8
    assert layout.get_offset("test3") == 15
    assert layout.get_slot_size() == 19


def test_can_create_layout_from_existing_offsets_and_slot_size():
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


def test_exception_raised_for_nonexistent_field_name():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    with pytest.raises(ValueError) as exc_info:
        layout.get_offset("test4")
    assert "Unknown field name test4" in str(exc_info.value)


def test_exception_raised_for_unknown_field_type():
    schema = Schema()
    schema.add_field("test1", 1, 1)
    schema.add_field("test2", 2, 3)
    schema.add_field("test3", 1, 4)

    layout = Layout(schema)

    with pytest.raises(KeyError):
        layout._length_in_bytes("test4")


def test_integer_field_layout_calculation():
    schema = Schema()
    schema.add_int_field("id")
    schema.add_int_field("age")
    schema.add_int_field("count")

    layout = Layout(schema)

    # 整数フィールドは4バイト
    assert layout.get_offset("id") == ByteSize.Int  # 4
    assert layout.get_offset("age") == ByteSize.Int + ByteSize.Int  # 8
    assert layout.get_offset("count") == ByteSize.Int + ByteSize.Int + ByteSize.Int  # 12
    assert layout.get_slot_size() == ByteSize.Int + 3 * ByteSize.Int  # 16


def test_string_field_layout_calculation():
    schema = Schema()
    schema.add_string_field("name", 10)
    schema.add_string_field("email", 50)

    layout = Layout(schema)

    # 文字列フィールドは長さ情報(4バイト) + 文字列長
    assert layout.get_offset("name") == ByteSize.Int  # 4
    assert layout.get_offset("email") == ByteSize.Int + Page.get_max_length(10)  # 4 + (4 + 10) = 18
    assert layout.get_slot_size() == ByteSize.Int + Page.get_max_length(10) + Page.get_max_length(50)


def test_mixed_field_type_layout():
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 20)
    schema.add_int_field("age")
    schema.add_string_field("address", 100)

    layout = Layout(schema)

    assert layout.get_offset("id") == 4
    assert layout.get_offset("name") == 8
    assert layout.get_offset("age") == 8 + Page.get_max_length(20)
    assert layout.get_offset("address") == 8 + Page.get_max_length(20) + 4


def test_get_schema():
    schema = Schema()
    schema.add_field("test", 1, 10)

    layout = Layout(schema)

    assert layout.get_schema() is schema


def test_empty_schema_layout():
    schema = Schema()
    layout = Layout(schema)

    # 空のスキーマでも最初の4バイトは予約される
    assert layout.get_slot_size() == ByteSize.Int
    assert layout.offsets == {}


def test_invalid_field_type():
    schema = Schema()
    # 不正なフィールドタイプ（1=Integer, 2=Varcharではない値）
    schema.add_field("invalid_field", 999, 10)

    # _length_in_bytesで例外が発生する
    with pytest.raises(ValueError) as exc_info:
        # layoutの初期化時にエラーが発生するはず
        layout = Layout(schema)
    assert "Unknown field type 999" in str(exc_info.value)


def test_layout_with_zero_length_fields():
    # 長さ0のフィールドのテスト
    schema = Schema()
    schema.add_field("zero_length", FieldType.Varchar, 0)
    schema.add_int_field("normal_int")

    layout = Layout(schema)

    # 長さ0の文字列フィールドでも最小限のバイト数が確保される
    assert layout.get_offset("zero_length") == 4
    assert layout.get_offset("normal_int") == 4 + Page.get_max_length(0)


def test_layout_memory_efficiency():
    # メモリ効率性の確認（大量フィールド）
    schema = Schema()
    num_fields = 100

    for i in range(num_fields):
        schema.add_int_field(f"field_{i}")

    layout = Layout(schema)

    # すべてのフィールドが正しくオフセットされている
    for i in range(num_fields):
        expected_offset = 4 + (i * 4)  # 4バイトごと
        assert layout.get_offset(f"field_{i}") == expected_offset

    expected_slot_size = 4 + (num_fields * 4)
    assert layout.get_slot_size() == expected_slot_size


def test_custom_offset_validation():
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 10)

    # カスタムオフセットを指定（通常の計算とは異なる値）
    custom_offsets = {"id": 10, "name": 20}
    custom_slot_size = 100

    layout = Layout(schema, custom_offsets, custom_slot_size)

    assert layout.get_offset("id") == 10
    assert layout.get_offset("name") == 20
    assert layout.get_slot_size() == 100


def test_offset_ordering():
    # フィールドの追加順序とオフセットの関係を確認
    schema = Schema()
    schema.add_int_field("first")
    schema.add_int_field("second")
    schema.add_string_field("third", 20)
    schema.add_int_field("fourth")

    layout = Layout(schema)

    # 各フィールドのオフセットが正しい順序で設定される
    assert layout.get_offset("first") < layout.get_offset("second")
    assert layout.get_offset("second") < layout.get_offset("third")
    assert layout.get_offset("third") < layout.get_offset("fourth")

    # 具体的な値も確認
    assert layout.get_offset("first") == 4
    assert layout.get_offset("second") == 8
    assert layout.get_offset("third") == 12
    assert layout.get_offset("fourth") == 12 + Page.get_max_length(20)


def test_partial_custom_offset():
    # offsetsまたはslot_sizeのどちらか一方だけがNoneの場合
    schema = Schema()
    schema.add_int_field("id")

    # offsetsだけNone
    layout1 = Layout(schema, None, 100)
    assert layout1.get_offset("id") == 4  # 計算される
    assert layout1.get_slot_size() == 8  # 計算される（slot_sizeパラメータは無視される）

    # slot_sizeだけNone
    layout2 = Layout(schema, {"id": 10}, None)
    assert layout2.get_offset("id") == 4  # 計算される
    assert layout2.get_slot_size() == 8  # 計算される
