import pytest
from unittest.mock import Mock
from db.transaction.buffer_list import BufferList
from db.buffer.buffer_manager import BufferManager
from db.file.block_id import BlockID
from db.buffer.buffer import Buffer

def test_指定されたブロックのバッファを取得できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)

    buffer_list.buffers[block] = buffer
    assert buffer_list.get_buffer(block) == buffer
    assert buffer_list.get_buffer(BlockID("testfile", 2)) is None

def test_ブロックをピン留めして追跡できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)
    buffer_manager.pin.return_value = buffer

    buffer_list.pin(block)

    assert buffer_list.buffers[block] == buffer
    assert block in buffer_list.pins
    buffer_manager.pin.assert_called_once_with(block)

def test_ブロックをアンピンして追跡から削除できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)
    buffer_list.buffers[block] = buffer
    buffer_list.pins.append(block)

    buffer_list.unpin(block)

    assert block not in buffer_list.pins
    assert block not in buffer_list.buffers
    buffer_manager.unpin.assert_called_once_with(buffer)

def test_すべてのブロックをアンピンして状態をリセットできる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    another_block = BlockID("testfile", 2)
    buffer = Mock(spec=Buffer)
    another_buffer = Mock(spec=Buffer)

    buffer_list.buffers[block] = buffer
    buffer_list.buffers[another_block] = another_buffer
    buffer_list.pins.extend([block, another_block])

    buffer_list.unpin_all()

    assert buffer_list.pins == []
    assert buffer_list.buffers == {}
    buffer_manager.unpin.assert_any_call(buffer)
    buffer_manager.unpin.assert_any_call(another_buffer)
