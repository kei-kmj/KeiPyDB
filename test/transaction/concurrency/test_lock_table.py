import threading
from unittest.mock import Mock

import pytest

from db.constants import LockMode
from db.file.block_id import BlockID
from db.transaction.concurrency.lock_table import LockAbortException, LockTable


def test_acquire_shared_lock():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_shared(block)

    assert lock_table.locks[block] == LockMode.Shared_Lock


def test_acquire_exclusive_lock():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_exclusive(block)

    assert lock_table.locks[block] == LockMode.Exclusive_Lock


def test_unlock_reduces_shared_lock_count():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_shared(block)
    lock_table.unlock(block)

    assert block not in lock_table.locks


def test_unlock_removes_exclusive_lock():
    lock_table = LockTable()
    block = BlockID("testfile", 0)

    lock_table.lock_exclusive(block)
    lock_table.unlock(block)

    assert block not in lock_table.locks


def test_shared_lock_fails_during_exclusive_lock():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_exclusive(block)

    with pytest.raises(LockAbortException):
        lock_table.lock_shared(block)


def test_exclusive_lock_fails_during_shared_lock():
    table = LockTable()
    block = BlockID("test", 0)
    table.MAX_TIME = 1

    table.lock_shared(block)

    def try_exclusive_lock():
        with pytest.raises(LockAbortException):
            table.lock_exclusive(block)
