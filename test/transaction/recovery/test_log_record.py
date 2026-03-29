from db.file.page import Page
from db.transaction.recovery.checkpoint_record import CheckpointRecord
from db.transaction.recovery.log_record import LogRecord


def test_record():
    page_data = bytearray(4)
    page = Page(page_data)
    page.set_int(0, LogRecord.CHECKPOINT)

    record = CheckpointRecord()
    assert isinstance(record, CheckpointRecord)
