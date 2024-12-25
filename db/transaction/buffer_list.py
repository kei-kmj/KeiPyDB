from typing import List, Optional

from db.buffer.buffer import Buffer
from db.buffer.buffer_manager import BufferManager
from db.file.block_id import BlockID


class BufferList:
    def __init__(self, buffer_manager: BufferManager) -> None:
        self.buffer_manager = buffer_manager
        self.buffers: dict[BlockID, Buffer] = {}
        self.pins: List[BlockID] = []

    def get_buffer(self, block: BlockID) -> Optional[Buffer]:
        return self.buffers.get(block)

    def pin(self, block: BlockID) -> None:
        buffer = self.buffer_manager.pin(block)
        self.buffers[block] = buffer
        self.pins.append(block)

    def unpin(self, block: BlockID) -> None:
        buffer = self.buffers.get(block)
        if buffer:
            self.buffer_manager.unpin(buffer)
            self.pins.remove(block)

            if block not in self.pins:
                del self.buffers[block]

    def unpin_all(self) -> None:
        for block in self.pins:
            buffer = self.buffers.get(block)
            if buffer:
                self.buffer_manager.unpin(buffer)
        self.buffers.clear()
        self.pins.clear()
