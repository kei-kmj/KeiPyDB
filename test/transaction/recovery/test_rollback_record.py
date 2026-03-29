from db.constants import ByteSize
from db.file.page import Page
from db.transaction.recovery.rollback_record import RollbackRecord


def test_record():
    # Setup mock Page
    page_data = bytearray(ByteSize.Int * 2)
    page = Page(page_data)
    transaction_id = 42
    page.set_int(ByteSize.Int, transaction_id)

    # Initialize RollbackRecord
    rollback_record = RollbackRecord(page)

    # Assertions
    assert rollback_record.tx_number() == transaction_id
    assert rollback_record.op() == RollbackRecord.ROLLBACK
    assert str(rollback_record) == f"<ROLLBACK {transaction_id}>"
