from db.file.block_id import BlockID


def test_new_block_id():
    file_name = "test"
    block_num = 1
    bid = BlockID(file_name, block_num)
    assert bid.file_name == file_name
    assert bid.number() == block_num


def test_block_id_equals():
    block_id = BlockID("test", 1)
    another_block_id = BlockID("test", 1)
    assert block_id == another_block_id


def test_block_id_not_equals():
    block_id = BlockID("test", 1)
    another_block_id = BlockID("test", 2)
    assert block_id != another_block_id


def test_block_id_string():
    block_id = BlockID("test", 1)
    assert str(block_id) == "[file test, block 1]"
