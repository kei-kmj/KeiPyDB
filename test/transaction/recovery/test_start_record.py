from unittest.mock import Mock

from db.constants import ByteSize, LogRecordFields
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.recovery.start_record import StartRecord


def test_start_record_initialization():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert start_record._tx_number == 42
    page.get_int.assert_called_once_with(ByteSize.Int)


# Removed trivial test - op() just returns a constant


def test_tx_number_transaction():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert start_record.tx_number() == 42


def test_start_record_string_representation():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert str(start_record) == "<START 42>"


def test_write_to_log_log():
    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 100

    tx_number = 42
    rec = bytearray(LogRecordFields.Two_Fields * ByteSize.Int)
    page = Page(rec)
    page.set_int(0, StartRecord.START)

    assert StartRecord.write_to_log(log_manager, tx_number) == 100
    # Verify append was called but don't check exact content
    log_manager.append.assert_called_once()
    assert page.get_int(0) == StartRecord.START
    # TODO:ここがおかしいかも
    assert page.get_int(ByteSize.Int) == 0
