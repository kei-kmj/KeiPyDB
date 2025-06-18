import pytest

from db.file.block_id import BlockID


def test_new_block_id():
    file_name = "test"
    block_num = 1
    bid = BlockID(file_name, block_num)
    assert bid.file_name == file_name
    assert bid.number() == block_num


def test_block_id_with_various_numbers():
    test_cases = [
        ("test.db", 0),
        ("myfile", 999999),
        ("data.txt", -1),
        ("", 42),
    ]
    
    for file_name, block_num in test_cases:
        bid = BlockID(file_name, block_num)
        assert bid.file_name == file_name
        assert bid.number() == block_num
        assert bid.block_number == block_num


def test_block_id_equals():
    block_id = BlockID("test", 1)
    another_block_id = BlockID("test", 1)
    assert block_id == another_block_id
    
    # 同じオブジェクトとの比較
    assert block_id == block_id


def test_block_id_not_equals():
    block_id = BlockID("test", 1)
    another_block_id = BlockID("test", 2)
    assert block_id != another_block_id
    
    # ファイル名が異なる場合
    different_file = BlockID("other", 1)
    assert block_id != different_file
    
    # 異なる型との比較
    assert block_id != "test"
    assert block_id != 1
    assert block_id != None


def test_block_id_string():
    block_id = BlockID("test", 1)
    assert str(block_id) == "[file test, block 1]"
    
    # 特殊なファイル名のケース
    special_cases = [
        ("", 0, "[file , block 0]"),
        ("file with spaces", 123, "[file file with spaces, block 123]"),
        ("日本語.db", 5, "[file 日本語.db, block 5]"),
    ]
    
    for file_name, block_num, expected in special_cases:
        bid = BlockID(file_name, block_num)
        assert str(bid) == expected


def test_block_id_hash():
    # 同じパラメータのBlockIDは同じハッシュ値を持つ
    bid1 = BlockID("test", 1)
    bid2 = BlockID("test", 1)
    assert hash(bid1) == hash(bid2)
    
    # 異なるパラメータのBlockIDは異なるハッシュ値を持つ（高確率で）
    bid3 = BlockID("test", 2)
    bid4 = BlockID("other", 1)
    assert hash(bid1) != hash(bid3)
    assert hash(bid1) != hash(bid4)
    
    # セットや辞書で使えることを確認
    block_set = {bid1, bid2, bid3}
    assert len(block_set) == 2  # bid1とbid2は同じ
    
    block_dict = {bid1: "value1", bid2: "value2"}
    assert len(block_dict) == 1  # bid1とbid2は同じキー
    assert block_dict[bid1] == "value2"
