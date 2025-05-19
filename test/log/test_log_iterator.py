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
        (0, 15, True),
        (0, 16, False),
        (1, 0, True),
    ],
)
def test_log_iterator_has_next(block_number, offset, expected, setup_file_manager):
    block_size = 16
    file_manager = setup_file_manager(block_size)

    log_iterator = LogIterator(file_manager, BlockID("file", block_number))
    log_iterator.current_offset = offset

    assert log_iterator.has_next() == expected


def test_log_iterator_raises_value_error_on_invalid_block(setup_file_manager):
    block_size = 16
    file_manager = setup_file_manager(block_size)

    file_name = "empty_log"
    page = Page(block_size)

    page.set_int(0, block_size)
    file_manager.write(BlockID(file_name, 0), page)

    log_iterator = LogIterator(file_manager, BlockID(file_name, 0))
    log_iterator.current_offset = block_size

    with pytest.raises(ValueError, match="Invalid block number: -1"):
        next(log_iterator)
