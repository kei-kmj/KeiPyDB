import pytest

from db.constants import ByteSize, FieldType
from db.record.schema import Schema


def test_can_add_field_to_schema():
    schema = Schema()
    schema.add_field("test", 4, 1)

    assert schema.get_fields() == ["test"]
    assert schema.get_type("test") == 4
    assert schema.get_length("test") == 1


def test_can_add_integer_field_to_schema():
    schema = Schema()
    schema.add_field("test", 4)

    assert schema.get_type("test") == 4
    assert schema.get_length("test") == 0


def test_can_add_string_field():
    schema = Schema()
    schema.add_field("test", 2, 10)

    assert schema.get_type("test") == 2
    assert schema.get_length("test") == 10


def test_can_add_field_based_on_other_schema():
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


def test_can_add_all_fields_from_other_schema():
    source_schema = Schema()
    source_schema.add_field("id", 4, 0)
    source_schema.add_field("name", 12, 50)

    target_schema = Schema()
    target_schema.add_all(source_schema)

    assert target_schema.get_fields() == ["id", "name"]
    assert target_schema.get_type("id") == 4
    assert target_schema.get_type("name") == 12
    assert target_schema.get_length("name") == 50


def test_can_check_if_field_exists_in_schema():
    schema = Schema()
    schema.add_field("test", 4, 1)

    assert schema.has_field("test") is True
    assert schema.has_field("test2") is False


def test_error_when_getting_type_of_nonexistent_field():
    schema = Schema()
    schema.add_field("test", 4, 1)

    with pytest.raises(KeyError):
        schema.get_type("nonexistent_field")

    with pytest.raises(KeyError):
        schema.get_length("nonexistent_field")


def test_add_int_field():
    schema = Schema()
    schema.add_int_field("user_id")
    
    assert schema.has_field("user_id")
    assert schema.get_type("user_id") == FieldType.Integer
    assert schema.get_length("user_id") == ByteSize.Int


def test_add_string_field():
    schema = Schema()
    schema.add_string_field("username", 50)
    
    assert schema.has_field("username")
    assert schema.get_type("username") == FieldType.Varchar
    assert schema.get_length("username") == 50


def test_multiple_field_addition_order_is_preserved():
    schema = Schema()
    field_names = ["id", "name", "age", "email", "created_at"]
    
    for i, field_name in enumerate(field_names):
        schema.add_field(field_name, 1, i)
    
    assert schema.get_fields() == field_names


def test_adding_same_field_name_multiple_times():
    schema = Schema()
    
    # 同じフィールド名を複数回追加
    schema.add_field("test", 1, 10)
    schema.add_field("test", 2, 20)
    
    # フィールドリストには重複して追加される（現在の実装）
    assert schema.get_fields() == ["test", "test"]
    
    # 情報は最後の値で上書きされる
    assert schema.get_type("test") == 2
    assert schema.get_length("test") == 20


def test_empty_schema():
    schema = Schema()
    
    assert schema.get_fields() == []
    assert not schema.has_field("any_field")
    
    with pytest.raises(KeyError):
        schema.get_type("any_field")


def test_field_info_internal_class():
    # FieldInfoクラスのテスト
    field_info = Schema.FieldInfo(FieldType.Varchar, 100)
    
    assert field_info.field_type == FieldType.Varchar
    assert field_info.length == 100


def test_complex_schema_combination():
    # 複数のスキーマを結合
    user_schema = Schema()
    user_schema.add_int_field("user_id")
    user_schema.add_string_field("username", 50)
    
    product_schema = Schema()
    product_schema.add_int_field("product_id")
    product_schema.add_string_field("product_name", 100)
    product_schema.add_int_field("price")
    
    order_schema = Schema()
    order_schema.add_int_field("order_id")
    order_schema.add("user_id", user_schema)
    order_schema.add("product_id", product_schema)
    order_schema.add_all(product_schema)  # すべてのproductフィールドも追加
    
    expected_fields = ["order_id", "user_id", "product_id", "product_id", "product_name", "price"]
    assert order_schema.get_fields() == expected_fields


def test_schema_edge_cases():
    """スキーマのエッジケーステスト"""
    schema = Schema()
    
    # 最大長の文字列フィールド
    schema.add_string_field("max_string", 65535)
    assert schema.get_length("max_string") == 65535
    
    # ゼロ長の文字列フィールド
    schema.add_string_field("empty_string", 0)
    assert schema.get_length("empty_string") == 0
    
    # 特殊文字を含むフィールド名
    special_names = ["_underscore", "field123", "a" * 100, "日本語フィールド"]
    for name in special_names:
        schema.add_int_field(name)
        assert schema.has_field(name)


def test_schema_performance_with_many_fields():
    """大量フィールドでのパフォーマンステスト"""
    schema = Schema()
    num_fields = 1000
    
    # 大量のフィールドを追加
    for i in range(num_fields):
        schema.add_int_field(f"field_{i}")
    
    # すべてのフィールドが正しく追加されていることを確認
    assert len(schema.get_fields()) == num_fields
    
    # ランダムなフィールドへのアクセス
    import random
    for _ in range(100):
        field_index = random.randint(0, num_fields - 1)
        field_name = f"field_{field_index}"
        assert schema.has_field(field_name)
        assert schema.get_type(field_name) == FieldType.Integer


def test_schema_immutability_concerns():
    """スキーマの不変性に関するテスト"""
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    
    # フィールドリストの直接操作（現在の実装では可能）
    fields_ref = schema.get_fields()
    original_length = len(fields_ref)
    
    # リストへの直接操作
    fields_ref.append("malicious_field")
    
    # スキーマの内部状態が変更されてしまう
    assert len(schema.get_fields()) == original_length + 1
    
    # しかしinfo辞書には情報がないのでhas_fieldはFalse
    assert not schema.has_field("malicious_field")


def test_schema_field_type_validation():
    """フィールドタイプの検証テスト"""
    schema = Schema()
    
    # 正常なフィールドタイプ
    schema.add_field("int_field", FieldType.Integer, 4)
    schema.add_field("varchar_field", FieldType.Varchar, 100)
    
    assert schema.get_type("int_field") == FieldType.Integer
    assert schema.get_type("varchar_field") == FieldType.Varchar
    
    # 不正なフィールドタイプでもエラーにならない（現在の実装）
    schema.add_field("invalid_field", 999, 10)
    assert schema.get_type("invalid_field") == 999


def test_schema_consistency_after_operations():
    """操作後のスキーマ一貫性テスト"""
    base_schema = Schema()
    base_schema.add_int_field("id")
    base_schema.add_string_field("name", 50)
    
    # 異なるスキーマを作成
    derived_schema = Schema()
    derived_schema.add_all(base_schema)
    derived_schema.add_string_field("email", 100)
    
    # 元のスキーマは変更されていない
    assert len(base_schema.get_fields()) == 2
    assert len(derived_schema.get_fields()) == 3
    
    # 各スキーマの独立性
    assert base_schema.has_field("id")
    assert base_schema.has_field("name")
    assert not base_schema.has_field("email")
    
    assert derived_schema.has_field("id")
    assert derived_schema.has_field("name")
    assert derived_schema.has_field("email")
