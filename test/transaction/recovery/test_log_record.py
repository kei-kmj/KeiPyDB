from db.file.page import Page
from db.transaction.recovery.checkpoint_record import CheckpointRecord
from db.transaction.recovery.log_record import LogRecord
from db.transaction.recovery.start_record import StartRecord


def test_チェックポイントレコードが作成されることを確認する():
    page_data = bytearray(4)  # CHECKPOINT has no additional data
    page = Page(page_data)
    page.set_int(0, LogRecord.CHECKPOINT)

    record = CheckpointRecord()
    assert isinstance(record, CheckpointRecord)

def test_スタートレコードが作成されることを確認する():
    page_data = bytearray(8)
    page = Page(page_data)
    page.set_int(0, LogRecord.START)
    page.set_int(4, 42)

    record = StartRecord(page)
    assert isinstance(record, StartRecord)

def test_コミットレコードが作成されることを確認する():
    page_data = bytearray(8)
    page = Page(page_data)
    page.set_int(0, LogRecord.COMMIT)
    record = StartRecord(page)

    assert isinstance(record, StartRecord)
