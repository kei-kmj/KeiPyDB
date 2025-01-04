import threading
import time
from typing import Dict

from db.constants import LockMode
from db.file.block_id import BlockID


class LockAbortException(Exception):
    pass


class LockTable:
    MAX_TIME = 10

    def __init__(self) -> None:
        self.locks: Dict[BlockID, int] = {}
        self.condition = threading.Condition()

    def lock_shared(self, block: BlockID) -> None:

        with self.condition:
            start_time = time.time()
            while self._has_exclusive_lock(block) and not self._waiting_too_long(start_time):
                self.condition.wait(self.MAX_TIME)

            if self._has_exclusive_lock(block):
                raise LockAbortException("Unable to acquire shared lock within the maximum wait time")

            current = self._get_lock_value(block)
            self.locks[block] = current + 1

    def lock_exclusive(self, block: BlockID) -> None:
        with self.condition:
            start_time = time.time()
            while self._has_other_shared_locks(block) and not self._waiting_too_long(start_time):
                self.condition.wait(self.MAX_TIME)

            if self._has_other_shared_locks(block):
                raise LockAbortException("Unable to acquire exclusive lock within the maximum wait time")

            self.locks[block] = LockMode.Exclusive_Lock

    def unlock(self, block: BlockID) -> None:
        with self.condition:
            if block not in self.locks:
                return

            current = self._get_lock_value(block)

            if current > 1:
                self.locks[block] = current - 1
            else:
                del self.locks[block]
                self.condition.notify_all()

    def _has_exclusive_lock(self, block: BlockID) -> bool:
        return self._get_lock_value(block) == LockMode.Exclusive_Lock

    def _has_other_shared_locks(self, block: BlockID) -> bool:
        return self._get_lock_value(block) == LockMode.Shared_Lock

    def _waiting_too_long(self, start_time: float) -> bool:
        return time.time() - start_time > self.MAX_TIME

    def _get_lock_value(self, block: BlockID) -> int:
        return self.locks.get(block, LockMode.No_Lock)
