from itertools import cycle
from unittest.mock import Mock

from db.constants import FieldType
from db.file.block_id import BlockID
from db.record.layout import Layout
from db.record.record_page import RecordPage
from db.record.schema import Schema
from db.transaction.transaction import Transaction


def test_整数値を正しく取得できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    transaction.get_int.return_value = 100
    assert page.get_int(0, "test") == 100


def test_文字列値を正しく取得できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 2, 10)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    transaction.get_string.return_value = "test"
    assert page.get_string(0, "test") == "test"


def test_整数値を正しく設定できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    page.set_int(0, "test", 100)
    transaction.set_int.assert_called_once_with(block, 4, 100)


def test_レコードを削除できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    page.delete(0)
    transaction.set_int.assert_called_once_with(block, 0, 0, True)


def test_フォーマット処理が正しく動作することを確認する():
    transaction = Mock(spec=Transaction)
    block = Mock(spec=BlockID)
    layout = Mock(spec=Layout)

    schema = Mock()
    schema.get_fields.return_value = ["field1", "field2"]
    # TODO: なぜcycleが必要なのか調べる
    schema.get_type.side_effect = cycle([FieldType.Integer, FieldType.Varchar])
    layout.get_schema.return_value = schema
    layout.get_offset.side_effect = cycle([4, 8])
    layout.get_slot_size.return_value = 16

    transaction.block_size.return_value = 64

    record_page = RecordPage(transaction, block, layout)
    record_page.format()

    transaction.set_int.assert_any_call(block, record_page._offset(0), RecordPage.EMPTY, False)
    transaction.set_int.assert_any_call(block, record_page._offset(0) + 4, 0, False)
    transaction.set_string.assert_any_call(block, record_page._offset(0) + 8, "", False)


def test_次の使用中スロットを検索できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    transaction.get_int.return_value = RecordPage.USED
    transaction.block_size.return_value = 128
    assert page.next_after(0) == 1


def test_次の空スロットを検索して設定できることを確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)

    transaction.get_int.return_value = RecordPage.EMPTY
    transaction.block_size.return_value = 128
    assert page.insert_after(0) == 1
    transaction.set_int.assert_called_once_with(block, 8, RecordPage.USED, True)


def test_スロットの有効性を確認する():
    transaction = Mock()
    block = BlockID("test", 1)
    schema = Schema()
    schema.add_field("test", 1, 1)
    layout = Layout(schema)
    page = RecordPage(transaction, block, layout)
    transaction.block_size.return_value = 128

    transaction.get_int.return_value = RecordPage.USED
    assert page._is_valid_slot(0) is True
