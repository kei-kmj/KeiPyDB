
from db.constants import LockType
from db.file.block_id import BlockID
from db.transaction.concurrency.lock_table import LockTable


class ConcurrencyManager:
    lock_table = LockTable()

    def __init__(self) -> None:
        self.locks: dict[BlockID, str] = {}
        self.lock_table = LockTable()

    def lock_shared(self, block: BlockID) -> None:
        if block not in self.locks:
            self.lock_table.lock_shared(block)
            self.locks[block] = LockType.Shared

    def lock_exclusive(self, block: BlockID) -> None:
        if not self.has_exclusive_lock(block):
            self.lock_shared(block)
            self.lock_table.lock_exclusive(block)
            self.locks[block] = LockType.Exclusive

    def release(self) -> None:
        for block in list(self.locks.keys()):
            self.lock_table.unlock(block)
        self.locks.clear()

    def has_exclusive_lock(self, block: BlockID) -> bool:
        return self.locks.get(block) == LockType.Exclusive
