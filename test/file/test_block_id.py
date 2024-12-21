from db.file.block_id import BlockID


def test_ブロックIDの等価性を検証():
    block = BlockID("testfile.txt", 5)
    other_block = BlockID("testfile.txt", 5)
    third_block = BlockID("otherfile.txt", 10)

    assert block == other_block
    assert block != third_block


def test_文字列表現の検証():
    block = BlockID("testfile.txt", 5)
    assert str(block) == "[testfile.txt, block 5]"
