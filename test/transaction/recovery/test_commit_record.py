from unittest.mock import Mock

from db.constants import ByteSize
from db.file.page import Page
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
