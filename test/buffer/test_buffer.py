import shutil
import tempfile
from unittest.mock import Mock

import pytest

from db.buffer.buffer import Buffer
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp()
    block_size = 400
    file_manager = FileManager(temp_dir, block_size)
    log_manager = LogManager(file_manager, "test_log")
    buffer = Buffer(file_manager, log_manager)

    yield buffer, file_manager

    shutil.rmtree(temp_dir)


def test_pin_unpin_behavior(test_env):
    buffer, _ = test_env

    assert not buffer.is_pinned()
    buffer.pin()
    assert buffer.is_pinned()
    buffer.unpin()
    assert not buffer.is_pinned()


def test_modifying_tx_tracking(test_env):
    buffer, _ = test_env
    assert buffer.modifying_tx() == -1
    buffer.set_modified(transaction_number=42, log_sequence_number=7)
    assert buffer.modifying_tx() == 42


def test_flush_calls_log_and_file_write():
    mock_file_manager = Mock()
    mock_file_manager.block_size = 400
    mock_log_manager = Mock()
    buffer = Buffer(mock_file_manager, mock_log_manager)

    buffer.block = BlockID("test_file", 0)
    buffer.contents.set_int(4, 12345)
    buffer.set_modified(transaction_number=42, log_sequence_number=99)

    buffer.flush()

    mock_log_manager.flush.assert_called_once_with(99)
    mock_file_manager.write.assert_called_once_with(buffer.block, buffer.contents)
    assert buffer.transaction_number == -1
