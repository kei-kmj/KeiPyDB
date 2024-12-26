from unittest.mock import Mock

import pytest

from db.constants import LockType
from db.file.block_id import BlockID
from db.transaction.concurrency.concurrency_manager import ConcurrencyManager


def test_共有ロックを取得できることを確認する():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_shared(block)

    assert manager.locks[block] == LockType.Shared


def test_排他ロックを取得できることを確認する():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_exclusive(block)

    assert manager.locks[block] == LockType.Exclusive


def test_共有ロックを取得したブロックに排他ロックを取得しようとすると例外が発生する():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_shared(block)

    with pytest.raises(Exception):
        manager.lock_exclusive(block)


def test_ロックを解放すると管理リストから削除されることを確認する():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_shared(block)
    manager.release()

    assert block not in manager.locks


def test_排他ロックが取得されているかを確認する():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_exclusive(block)

    assert manager.has_exclusive_lock(block)
