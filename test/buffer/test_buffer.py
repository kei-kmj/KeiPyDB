import pytest
from unittest.mock import Mock
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_manager import LogManager
from db.buffer.buffer import Buffer

def test_ブロックを割り当てられる():
    file_manager = Mock(spec=FileManager)
    log_manager = Mock(spec=LogManager)
    file_manager.block_size = 1024
    file_manager.read = Mock()

    block = BlockID("testfile", 1)
    buffer = Buffer(file_manager, log_manager)

    buffer.assign_to_block(block)

    assert buffer.block == block
    assert buffer.pins == 0
    file_manager.read.assert_called_once_with(block, buffer.contents)

def test_バッファをフラッシュできる():
    file_manager = Mock(spec=FileManager)
    log_manager = Mock(spec=LogManager)
    file_manager.block_size = 1024

    block = BlockID("testfile", 1)
    buffer = Buffer(file_manager, log_manager)

    buffer.assign_to_block(block)
    buffer.set_modified(42, 100)

    buffer.flush()

    log_manager.flush.assert_called_once_with(100)
    file_manager.write.assert_called_once_with(block, buffer.contents)
    assert buffer.transaction_number == -1

def test_ピンとアンピンが動作する():
    file_manager = Mock(spec=FileManager)
    log_manager = Mock(spec=LogManager)
    file_manager.block_size = 1024

    buffer = Buffer(file_manager, log_manager)

    buffer.pin()
    assert buffer.pins == 1

    buffer.unpin()
    assert buffer.pins == 0

def  test_修正状態を設定できる():
    file_manager = Mock(spec=FileManager)
    log_manager = Mock(spec=LogManager)
    file_manager.block_size = 1024

    buffer = Buffer(file_manager, log_manager)

    buffer.set_modified(42, 100)

    assert buffer.transaction_number == 42
    assert buffer.log_sequence_number == 100
