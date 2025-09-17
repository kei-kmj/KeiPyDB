import pytest

from db.record.record_id import RecordID


def test_new_record_id():
    block_num = 10
    slot = 5
    rid = RecordID(block_num, slot)

    assert rid.block_number == block_num
    assert rid.slot == slot
    assert rid.get_block_number() == block_num
    assert rid.get_slot() == slot


def test_record_id_with_various_values():
    test_cases = [
        (0, 0),
        (1, 100),
        (999999, 999999),
        (-1, -1),  # 負の値も許可されている
        (100, -5),
    ]

    for block_num, slot in test_cases:
        rid = RecordID(block_num, slot)
        assert rid.block_number == block_num
        assert rid.slot == slot


def test_record_id_equals():
    rid1 = RecordID(10, 5)
    rid2 = RecordID(10, 5)
    rid3 = RecordID(10, 5)

    assert rid1 == rid2
    assert rid2 == rid3
    assert rid1 == rid3

    # 同じオブジェクトとの比較
    assert rid1 == rid1


def test_record_id_not_equals():
    rid1 = RecordID(10, 5)
    rid2 = RecordID(10, 6)  # 異なるスロット
    rid3 = RecordID(11, 5)  # 異なるブロック
    rid4 = RecordID(11, 6)  # 両方異なる

    assert rid1 != rid2
    assert rid1 != rid3
    assert rid1 != rid4

    # 異なる型との比較
    assert rid1 != "test"
    assert rid1 != 10
    assert rid1 != None
    assert rid1 != (10, 5)


def test_record_id_repr():
    rid = RecordID(10, 5)
    assert repr(rid) == "[block 10, slot 5]"

    # 特殊なケース
    special_cases = [
        (0, 0, "[block 0, slot 0]"),
        (-1, -1, "[block -1, slot -1]"),
        (12345, 67890, "[block 12345, slot 67890]"),
    ]

    for block_num, slot, expected in special_cases:
        rid = RecordID(block_num, slot)
        assert repr(rid) == expected


# Removed test_record_id_hash_consistency - RecordID doesn't implement __hash__


def test_record_id_mutability():
    # RecordIDの属性は初期化後に変更可能（現在の実装では）
    rid = RecordID(10, 5)

    # 属性を変更できることを確認
    rid.block_number = 20
    rid.slot = 15

    assert rid.get_block_number() == 20
    assert rid.get_slot() == 15
    assert repr(rid) == "[block 20, slot 15]"


def test_record_id_edge_cases():
    # エッジケースのテスト
    edge_cases = [
        (0, 0),
        (2**31 - 1, 2**31 - 1),  # 最大の正の整数
        (-(2**31), -(2**31)),  # 最小の負の整数
    ]

    for block_num, slot in edge_cases:
        rid = RecordID(block_num, slot)
        assert rid.get_block_number() == block_num
        assert rid.get_slot() == slot
        assert rid == RecordID(block_num, slot)


def test_record_id_type_checking():
    # 異なる型との比較テスト
    rid = RecordID(1, 2)

    non_record_objects = [
        None,
        1,
        "string",
        [1, 2],
        {"block_number": 1, "slot": 2},
        object(),
        (1, 2),
    ]

    for obj in non_record_objects:
        assert rid != obj
        assert not (rid == obj)


def test_record_id_construction_type_safety():
    # 型安全性のテスト（現在のPythonでは実行時チェックなし）
    # float値でもintに変換される場合がある
    rid_float = RecordID(10.0, 5.0)
    assert rid_float.block_number == 10.0
    assert rid_float.slot == 5.0

    # 文字列も渡せてしまう（現在の実装では）
    rid_str = RecordID("10", "5")
    assert rid_str.block_number == "10"
    assert rid_str.slot == "5"
