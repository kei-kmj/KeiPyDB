from unittest.mock import Mock

from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.recovery.checkpoint_record import CheckpointRecord
from db.transaction.transaction import Transaction


def test_チェックポイントレコードの初期化を確認する():
    checkpoint = CheckpointRecord()
    assert checkpoint.CHECKPOINT == 2
    assert str(checkpoint) == "<CHECKPOINT>"


def test_チェックポイントレコードのトランザクションIDがダミー値であることを確認する():
    assert CheckpointRecord.tx_number() == -1


def test_ログへのチェックポイントレコード書き込みを確認する():
    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 123  # Mock LSN

    lsn = CheckpointRecord.write_to_log(log_manager)

    assert lsn == 123
    log_manager.append.assert_called_once()

    appended_data = log_manager.append.call_args[0][0]
    page = Page(appended_data)
    assert page.get_int(0) == 0
