from unittest.mock import Mock

from db.constants import ByteSize, LogRecordFields
from db.file.page import Page
from db.log.log_manager import LogManager
from db.transaction.recovery.start_record import StartRecord


def test_スタートレコードが正しく初期化されること():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert start_record._tx_number == 42
    page.get_int.assert_called_once_with(ByteSize.Int)


def test_opメソッドがスタート操作コードを返すこと():
    page = Mock(spec=Page)
    start_record = StartRecord(page)

    assert start_record.op() == StartRecord.START


def test_tx_numberメソッドがトランザクション番号を返すこと():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert start_record.tx_number() == 42


def test_スタートレコードの文字列表現が正しいこと():
    page = Mock(spec=Page)
    page.get_int.return_value = 42

    start_record = StartRecord(page)

    assert str(start_record) == "<START 42>"


def test_write_to_logが正しいデータをログに書き込むこと():
    log_manager = Mock(spec=LogManager)
    log_manager.append.return_value = 100

    tx_number = 42
    rec = bytearray(LogRecordFields.Two_Fields * ByteSize.Int)
    page = Page(rec)
    page.set_int(0, StartRecord.START)

    assert StartRecord.write_to_log(log_manager, tx_number) == 100
    log_manager.append.assert_called_once_with(rec)
    assert page.get_int(0) == StartRecord.START
    # TODO:ここがおかしいかも
    assert page.get_int(ByteSize.Int) == 0
