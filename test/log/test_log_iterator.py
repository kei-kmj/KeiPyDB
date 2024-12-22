import pytest
from unittest.mock import Mock
from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_iterator import LogIterator


def test_初期化時に正しいブロックが読み込まれること():
    mock_file_manager = Mock(spec=FileManager)
    mock_page = Mock(spec=Page)
    mock_file_manager.block_size = 1024
    mock_block = BlockID("testfile", 2)

    log_iterator = LogIterator(mock_file_manager, mock_block)

    mock_file_manager.read.assert_called_once_with(mock_block, log_iterator.page)


def test_次のレコードを正しく取得できること():
    mock_file_manager = Mock(spec=FileManager)
    mock_page = Mock(spec=Page)
    mock_file_manager.block_size = 1024
    mock_block = BlockID("testfile", 2)

    mock_page.get_bytes.return_value = b"test_record"
    mock_page.get_int.return_value = 0

    log_iterator = LogIterator(mock_file_manager, mock_block)
    log_iterator.page = mock_page

    record = next(log_iterator)

    assert record == b"test_record"
    assert log_iterator.current_position == ByteSize.Int + len(record)


def test_レコードが存在しない場合StopIterationが発生すること():
    mock_file_manager = Mock(spec=FileManager)
    mock_page = Mock(spec=Page)
    mock_file_manager.block_size = 1024
    mock_block = BlockID("testfile", 2)

    mock_page.get_bytes.side_effect = StopIteration
    mock_page.get_int.return_value = 1024  # Boundary outside the range

    log_iterator = LogIterator(mock_file_manager, mock_block)
    log_iterator.page = mock_page

    with pytest.raises(StopIteration):
        next(log_iterator)


def test_次のブロックに移動できること():
    mock_file_manager = Mock(spec=FileManager)
    mock_page = Mock(spec=Page)
    mock_file_manager.block_size = 1024
    mock_block = BlockID("testfile", 2)

    mock_page.get_bytes.return_value = b"test_record"
    mock_page.get_int.return_value = 0

    log_iterator = LogIterator(mock_file_manager, mock_block)
    log_iterator.page = mock_page

    record = next(log_iterator)
    assert record == b"test_record"

    mock_page.get_bytes.return_value = b"test_record2"
    mock_page.get_int.return_value = 0

    record = next(log_iterator)
    assert record == b"test_record2"
    assert log_iterator.current_position == ByteSize.Int + len(b"test_record") + ByteSize.Int + len(b"test_record2")


