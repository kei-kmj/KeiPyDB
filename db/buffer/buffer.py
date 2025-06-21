from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_manager import LogManager


class Buffer:
    def __init__(self, file_manager: FileManager, log_manager: LogManager) -> None:
        self.file_manager = file_manager
        self.log_manager = log_manager
        self.contents = Page(self.file_manager.block_size)
        self.block = None
        self.pins = 0
        self.transaction_number = -1
        self.log_sequence_number = -1

    def get_contents(self) -> Page:
        return self.contents

    def set_modified(self, transaction_number: int, log_sequence_number: int) -> None:
        self.transaction_number = transaction_number
        if log_sequence_number >= 0:
            self.log_sequence_number = log_sequence_number

    def assign_to_block(self, block: BlockID) -> None:
        self.flush()
        self.block = block
        self.file_manager.read(self.block, self.contents)
        self.pins = 0

    def flush(self) -> None:
        if self.transaction_number >= 0 and self.transaction_number is not None:
            self.log_manager.flush(self.log_sequence_number)
            self.file_manager.write(self.block, self.contents)
            self.transaction_number = -1

    def pin(self) -> None:


        self.pins += 1

    def unpin(self) -> None:
        self.pins -= 1

    def is_pinned(self) -> bool:
        return self.pins > 0

    def modifying_tx(self) -> int:
        return self.transaction_number
