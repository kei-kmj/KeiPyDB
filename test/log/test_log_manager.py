import pytest
from unittest.mock import Mock
from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_manager import LogManager
from db.log.log_iterator import LogIterator


def test_初期化時にブロックが作成されること():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_file_manager.length.return_value = 0
    mock_file_manager.append.return_value = BlockID("testfile", 0)

    log_manager = LogManager(mock_file_manager, "testfile")

    assert log_manager.current_block == BlockID("testfile", 0)
    mock_file_manager.append.assert_called_once_with("testfile")


def test_初期化時に既存ブロックを読み込むこと():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_page = Mock(spec=Page)
    mock_file_manager.length.return_value = 1
    mock_file_manager.read.return_value = None

    log_manager = LogManager(mock_file_manager, "testfile")
    log_manager.log_page = mock_page

    assert log_manager.current_block == BlockID("testfile", 0)


def test_appendでレコードが正しく追加されること():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_page = Mock(spec=Page)
    mock_file_manager.length.return_value = 1
    mock_page.get_int.return_value = 1024

    log_manager = LogManager(mock_file_manager, "testfile")
    log_manager.log_page = mock_page

    lsn = log_manager.append(b"test_record")

    assert lsn == 1
    mock_page.set_bytes.assert_called_once()
    mock_page.set_int.assert_called_with(0, 1024 - (len(b"test_record") + ByteSize.Int))


def test_appendで新しいブロックが作成されること():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_page = Mock(spec=Page)
    mock_file_manager.length.return_value = 1
    mock_file_manager.append.return_value = BlockID("testfile", 1)
    mock_page.get_int.side_effect = [4, 1024]  # 最初のブロックが一杯で次のブロックを作成

    log_manager = LogManager(mock_file_manager, "testfile")
    log_manager.log_page = mock_page

    lsn = log_manager.append(b"test_record")

    assert lsn == 1
    assert log_manager.current_block == BlockID("testfile", 1)
    mock_file_manager.append.assert_called_once_with("testfile")
    mock_file_manager.write.assert_called()


def test_iteratorでLogIteratorを返すこと():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_page = Mock(spec=Page)
    mock_file_manager.length.return_value = 1
    mock_page.get_int.return_value = 1024

    log_manager = LogManager(mock_file_manager, "testfile")
    log_manager.log_page = mock_page

    iterator = log_manager.iterator()

    assert isinstance(iterator, LogIterator)
    assert iterator.file_manager == mock_file_manager
    assert iterator.block == BlockID("testfile", 0)


def test_flushでデータが保存されること():
    mock_file_manager = Mock(spec=FileManager)
    mock_file_manager.block_size = 1024
    mock_page = Mock(spec=Page)
    mock_file_manager.length.return_value = 1
    mock_page.get_int.return_value = 1024

    log_manager = LogManager(mock_file_manager, "testfile")
    log_manager.log_page = mock_page

    log_manager.flush(1)

    mock_file_manager.write.assert_called_once_with(BlockID("testfile", 0), mock_page)
