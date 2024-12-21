from threading import Lock

from db.buffer.buffer import Buffer
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


class BufferManager:
    def __init__(self, file_manager: FileManager, log_manager: LogManager, num_buffers: int) -> None:
        self.file_manager = file_manager
        self.log_manager = log_manager
        self.buffer_pool = [Buffer(file_manager, log_manager) for _ in range(num_buffers)]
        self.num_available = num_buffers
        self.lock = Lock()

    def available(self) -> int:
        with self.lock:
            return self.num_available

    def flush_all(self, tx_num) -> None:
        with self.lock:
            for buffer in self.buffer_pool:
                if buffer.modifying_tx == tx_num:
                    buffer.flush()

    def unpin(self, buffer: Buffer) -> None:
        with self.lock:
            buffer.unpin()
            if not buffer.is_pinned():
                self.num_available += 1

    def pin(self, block: BlockID) -> Buffer:
        with self.lock:
            buffer = self._try_to_pin(block)
            if buffer:
                return buffer

    def _try_to_pin(self, block: BlockID) -> Buffer:
        pass
