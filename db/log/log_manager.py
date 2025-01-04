from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_iterator import LogIterator


class LogManager:
    def __init__(self, file_manager: FileManager, log_file: str) -> None:
        self.file_manager = file_manager
        self.log_file = log_file
        self.log_page = Page(file_manager.block_size)
        self.current_block = None
        self.current_lsn = 0
        self.last_saved_lsn = 0

        log_size = self.file_manager.length(log_file)

        if log_size == 0:
            self.current_block = self.file_manager.append(log_file)
        else:
            self.current_block = BlockID(log_file, log_size - 1)
            self.file_manager.read(self.current_block, self.log_page)

    def flush(self, lsn: int) -> None:
        if lsn >= self.last_saved_lsn:
            self._flush()

    def iterator(self) -> LogIterator:
        self._flush()

        if self.current_block is None:
            raise ValueError("No log records to read")

        return LogIterator(self.file_manager, self.current_block)

    def append(self, log_record: bytes) -> int:
        boundary = self.log_page.get_int(0)
        record_size = len(log_record)
        bytes_needed = record_size + ByteSize.Int

        if boundary - bytes_needed < ByteSize.Int:
            self._flush()
            self.current_block = self._append_new_block()
            boundary = self.log_page.get_int(0)

        record_position = boundary - bytes_needed
        self.log_page.set_bytes(record_position, log_record)
        self.log_page.set_int(0, record_position)
        self.current_lsn += 1
        return self.current_lsn

    def _append_new_block(self) -> BlockID:
        block = self.file_manager.append(self.log_file)
        self.log_page.set_int(0, self.file_manager.block_size)
        self.file_manager.write(block, self.log_page)
        return block

    def _flush(self) -> None:
        if self.current_block is None:
            raise ValueError("Current block is not set.")

        self.file_manager.write(self.current_block, self.log_page)
        self.last_saved_lsn = self.current_lsn
