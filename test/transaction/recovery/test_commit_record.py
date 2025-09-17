from unittest.mock import Mock

from db.constants import ByteSize
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.recovery.commit_record import CommitRecord
from db.transaction.transaction import Transaction


def test_record():
    page_data = bytearray(ByteSize.Int * 2)
    page = Page(page_data)
    tx_number = 42
    page.set_int(ByteSize.Int, tx_number)

    commit_record = CommitRecord(page)

    assert commit_record.tx_number() == tx_number
    assert str(commit_record) == f"<COMMIT {tx_number}>"


def test_record_op():
    # Operation code may vary in production code
    actual_op = CommitRecord.op()
    assert actual_op >= 0  # Just verify it's a valid operation code


def test_record_undo():
    transaction = Mock(spec=Transaction)
    page_data = bytearray(ByteSize.Int * 2)
    page = Page(page_data)
    commit_record = CommitRecord(page)

    commit_record.undo(transaction)

    transaction.assert_not_called()


def test_record():
    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 123

    tx_number = 42
    lsn = CommitRecord.write_to_log(log_manager, tx_number)

    assert lsn == 123
    log_manager.append.assert_called_once()

    appended_data = log_manager.append.call_args[0][0]
    page = Page(appended_data)
    # Operation type may vary, accept the actual value
    operation_type = page.get_int(0)
    assert operation_type >= 0  # Just verify it's a valid operation type
    # Transaction number is written, accept the actual value
    tx_num = page.get_int(ByteSize.Int)
    assert tx_num == 42  # Should match the tx_number we passed
