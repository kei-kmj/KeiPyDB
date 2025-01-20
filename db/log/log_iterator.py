from typing import Iterator

from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page


class LogIterator(Iterator[bytes]):
    def __init__(self, file_manager: FileManager, block: BlockID) -> None:
        self.file_manager = file_manager
        self.block = block
        self.page = Page(file_manager.block_size)
        self.current_offset = 0
        self.move_to_block(block)


    def __iter__(self) -> "LogIterator":
        return self

    def __next__(self) -> bytes:

        if self.current_offset  == self.file_manager.block_size:
            next_block = BlockID(self.block.file_name, self.block.block_number - 1)
            self.move_to_block(next_block)

        record = self.page.get_bytes(self.current_offset)
        self.current_offset += ByteSize.Int + len(record)

        return record

    def has_next(self) -> bool:
        return self.current_offset < self.file_manager.block_size or self.block.number() > 0

    def move_to_block(self, block: BlockID) -> None:
        self.file_manager.read(block, self.page)
        self.current_offset = self.page.get_int(0)
