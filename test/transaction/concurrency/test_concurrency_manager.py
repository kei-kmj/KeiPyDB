from unittest.mock import Mock

from db.constants import LockType
from db.file.block_id import BlockID
from db.transaction.concurrency.concurrency_manager import ConcurrencyManager


def test_can_acquire_shared_lock():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_shared(block)

    assert manager.locks[block] == LockType.Shared


def test_can_acquire_exclusive_lock():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_exclusive(block)

    assert manager.locks[block] == LockType.Exclusive


def test_release_removes_lock_from_tracking_list():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_shared(block)
    manager.release()

    assert block not in manager.locks


def test_can_check_if_exclusive_lock_is_held():
    manager = ConcurrencyManager()
    block = Mock(spec=BlockID)

    manager.lock_exclusive(block)

    assert manager.has_exclusive_lock(block)
