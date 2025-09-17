import time
from threading import Condition
from typing import Optional

from db.buffer.buffer import Buffer
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


class BufferAbortException(Exception):
    pass


class BufferManager:
    MAX_TIME = 100

    def __init__(self, file_manager: FileManager, log_manager: LogManager, num_buffers: int) -> None:
        self.file_manager = file_manager
        self.log_manager = log_manager
        self.buffer_pool = [Buffer(file_manager, log_manager) for _ in range(num_buffers)]
        self.num_available = num_buffers
        self.condition = Condition()

    def available(self) -> int:
        with self.condition:
            return self.num_available

    def flush_all(self, tx_num: int) -> None:
        """指定されたトランザクションの全バッファをフラッシュ"""
        with self.condition:
            # バッファのスナップショットを取得
            buffers_to_flush = []
            for buffer in self.buffer_pool:
                # Bufferクラス内でもロックが必要
                if buffer.modifying_tx() == tx_num:
                    buffers_to_flush.append(buffer)

            # ロックを保持したままフラッシュ
            for buffer in buffers_to_flush:
                buffer.flush()

    def unpin(self, buffer: Buffer) -> None:
        with self.condition:
            buffer.unpin()
            if not buffer.is_pinned():
                self.num_available += 1
                self.condition.notify_all()

    def pin(self, block: BlockID) -> Buffer:
        with self.condition:
            time_stamp = time.time()
            buffer = self._try_to_pin(block)

            while buffer is None and not self._waiting_too_long(time_stamp):
                try:
                    self.condition.wait(self.MAX_TIME)
                    buffer = self._try_to_pin(block)
                except KeyboardInterrupt:
                    raise BufferAbortException()

            if buffer is None:
                raise BufferAbortException()

            return buffer

    def _waiting_too_long(self, time_stamp: float) -> bool:
        return time.time() - time_stamp >= self.MAX_TIME

    def _try_to_pin(self, block: BlockID) -> Optional[Buffer]:
        buffer = self._find_existing_buffer(block)
        if buffer is None:
            buffer = self._choose_unpinned_buffer()
            if buffer is None:
                return None
            buffer.assign_to_block(block)

        if not buffer.is_pinned():
            self.num_available -= 1

        buffer.pin()
        return buffer

    def _find_existing_buffer(self, block: BlockID) -> Optional[Buffer]:
        """既存のバッファを検索"""
        for buffer in self.buffer_pool:
            buffer_block = buffer.block
            if buffer_block is not None and buffer_block == block:
                return buffer
        return None

    def _choose_unpinned_buffer(self) -> Optional[Buffer]:
        for buffer in self.buffer_pool:
            if not buffer.is_pinned():
                return buffer
        return None
