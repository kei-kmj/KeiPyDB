from unittest.mock import Mock

from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.recovery.checkpoint_record import CheckpointRecord


def test_checkpoint_record_initialization():
    checkpoint = CheckpointRecord()
    assert checkpoint.CHECKPOINT == 0
    assert str(checkpoint) == "<CHECKPOINT>"


def test_checkpoint_record_tx_number_is_dummy():
    assert CheckpointRecord.tx_number() == -1


def test_checkpoint_record_write_to_log():
    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 123

    lsn = CheckpointRecord.write_to_log(log_manager)

    assert lsn == 123
    log_manager.append.assert_called_once()

    appended_data = log_manager.append.call_args[0][0]
    page = Page(appended_data)
    assert page.get_int(0) == 0
