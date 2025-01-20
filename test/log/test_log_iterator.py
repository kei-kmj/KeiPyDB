from importlib.metadata import files
from math import log10

import pytest

from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_iterator import LogIterator


@pytest.fixture
def setup_file_manager(tmp_path):
    """一時ディレクトリとFileManagerをセットアップ"""
    def _setup(block_size):
        db_directory = tmp_path / "test_log_iterator"
        db_directory.mkdir()
        return FileManager(db_directory, block_size)
    return _setup


@pytest.mark.parametrize(
    "block_number, offset, expected",
    [
        (0, 15, True),   # オフセットがブロックサイズ未満
        (0, 16, False),  # オフセットがブロックサイズと同じ
        (1, 0, True),      # ブロック番号が0より大きい場合
    ],
)
def test_log_iterator_has_next(block_number, offset, expected, setup_file_manager):
    block_size = 16
    file_manager = setup_file_manager(block_size)

    log_iterator = LogIterator(file_manager, BlockID("file", block_number))
    log_iterator.current_offset = offset

    assert log_iterator.has_next() == expected


def test_log_iterator_next_not_finished(setup_file_manager):
    block_size = 14
    file_manager = setup_file_manager(block_size)

    file_name = "log_file"
    record = b"record"
    page = Page(block_size)

    page.set_int(0, 4)
    page.set_bytes(4, record)
    file_manager.write(BlockID(file_name, 3), page)

    log_iterator = LogIterator(file_manager, BlockID(file_name, 3))

    result = log_iterator.__next__()

    assert result == record
