import os
import tempfile
import shutil

import pytest

from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


@pytest.fixture
def temp_log_env():
    temp_dir = tempfile.mkdtemp()
    block_size = 1024
    file_manager = FileManager(temp_dir, block_size)
    log_file = "test_log"
    log_manager = LogManager(file_manager, log_file)

    yield log_manager, file_manager, log_file

    shutil.rmtree(temp_dir)


def test_append_increases_lsn(temp_log_env):
    log_manager, *_ = temp_log_env
    initial_lsn = log_manager.current_lsn
    lsn = log_manager.append(b"test record")
    assert lsn == initial_lsn + 1


def test_flush_writes_to_disk(temp_log_env):
    log_manager, file_manager, log_file = temp_log_env
    log_manager.append(b"test record")
    lsn = log_manager.current_lsn
    log_manager.flush(lsn)

    # 明示的な flush によって last_saved_lsn が更新されていることを確認
    assert log_manager.last_saved_lsn == lsn


def test_append_new_block_if_not_enough_space(temp_log_env):
    log_manager, file_manager, log_file = temp_log_env

    large_record = b"x" * (file_manager.block_size - 8)
    log_manager.append(large_record)

    prev_block = log_manager.current_block
    log_manager.append(b"tiny")
    new_block = log_manager.current_block

    assert prev_block != new_block
