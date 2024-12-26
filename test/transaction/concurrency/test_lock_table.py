from unittest.mock import Mock

import pytest

from db.constants import LockMode
from db.file.block_id import BlockID
from db.transaction.concurrency.lock_table import LockAbortException, LockTable


def test_共有ロックが取得できることを確認する():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_shared(block)

    assert lock_table.locks[block] == LockMode.Shared_Lock


def test_排他ロックが取得できることを確認する():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_exclusive(block)

    assert lock_table.locks[block] == LockMode.Exclusive_Lock


def test_共有ロックが解除されることを確認する():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_shared(block)
    lock_table.unlock(block)

    assert block not in lock_table.locks


def test_排他ロックが解除されることを確認する():
    lock_table = LockTable()
    block = BlockID("testfile", 0)

    lock_table.lock_exclusive(block)
    lock_table.unlock(block)

    assert block not in lock_table.locks


def test_排他ロック取得中に共有ロックが取得できないことを確認する():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_exclusive(block)

    with pytest.raises(LockAbortException):
        lock_table.lock_shared(block)


def test_共有ロック取得中に排他ロックが取得できないことを確認する():
    lock_table = LockTable()
    block = Mock(spec=BlockID)

    lock_table.lock_shared(block)

    with pytest.raises(LockAbortException):
        lock_table.lock_exclusive(block)
