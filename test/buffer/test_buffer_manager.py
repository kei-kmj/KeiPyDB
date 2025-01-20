from unittest.mock import Mock

import pytest

from db.buffer.buffer_manager import BufferAbortException, BufferManager
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


def test_利用可能なバッファの数を取得できる():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    assert buffer_manager.available() == 3


def test_バッファをフラッシュできる():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)
    buffer = buffer_manager._choose_unpinned_buffer()
    buffer.assign_to_block(block)
    buffer.set_modified(42, 100)

    buffer_manager.flush_all(42)

    log_manager.flush.assert_called_once_with(100)
    file_manager.write.assert_called_once_with(block, buffer.contents)


def test_ブロックをピンできる():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager.pin(block)

    assert buffer.block == block
    assert buffer.pins == 1


def test_ブロックをアンピンできる():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager.pin(block)
    buffer_manager.unpin(buffer)

    assert buffer.pins == 0
    assert buffer_manager.available() == 3


@pytest.mark.skip
def test_タイムアウトで例外が発生する():
    file_manager = Mock(spec=FileManager)
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=0)

    block = BlockID("testfile", 1)

    with pytest.raises(BufferAbortException):
        buffer_manager.pin(block)


def test_利用可能なバッファを探せる():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager._choose_unpinned_buffer()
    buffer.assign_to_block(block)

    found_buffer = buffer_manager._find_existing_buffer(block)

    assert found_buffer == buffer
