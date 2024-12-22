from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page


class LogIterator:
    def __init__(self, file_manager: FileManager, block: BlockID) -> None:
        self.file_manager = file_manager
        self.block = block
        self.page = Page(file_manager.block_size)
        self.current_position = 0
        self.boundary = 0

        self._move_to_block(block)

    def __iter__(self) -> "LogIterator":
        return self

    def __next__(self) -> bytes:
        if not self.has_next():
            raise StopIteration

        if self.current_position == self.file_manager.block_size:
            self.block = BlockID(self.block.file_name, self.block.block_number - 1)
            self._move_to_block(self.block)

        record = self.page.get_bytes(self.current_position)
        self.current_position += ByteSize.Int + len(record)

        return record

    def has_next(self) -> bool:
        return self.current_position < self.file_manager.block_size or self.block.block_number > 0

    def _move_to_block(self, block: BlockID) -> None:
        self.file_manager.read(block, self.page)
        self.boundary = self.page.get_int(0)
        self.current_position = self.boundary
        self.block = block