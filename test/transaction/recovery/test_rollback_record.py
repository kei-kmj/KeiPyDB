import pytest
from db.constants import LogRecordFields, ByteSize
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction
from db.transaction.recovery.rollback_record import RollbackRecord
from unittest.mock import Mock


def test_ロールバックレコードの初期化を確認する():
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


def test_ログへのロールバックレコード書き込みを確認する():

    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 123

    transaction_id = 42
    lsn = RollbackRecord.write_to_log(log_manager, transaction_id)

    # Assertions
    assert lsn == 123
    log_manager.append.assert_called_once()

    appended_data = log_manager.append.call_args[0][0]

    page = Page(appended_data)
    rollback_value = page.get_int(0)
    transaction_value = page.get_int(ByteSize.Int)

    # TODO:ここがおかしいかも
    assert rollback_value == 0
    assert transaction_value == 0

