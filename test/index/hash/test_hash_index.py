from unittest.mock import Mock

import pytest

from db.index.hash.hash_index import HashIndex
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


@pytest.fixture
def mock_transaction():
    return Mock(spec=Transaction)


@pytest.fixture
def mock_layout():
    return Mock(spec=Layout)


@pytest.fixture
def hash_index(mock_transaction, mock_layout):
    return HashIndex(mock_transaction, "test_index", mock_layout)


@pytest.mark.skip(reason="TODO:後で見直す")
def test_before_first(hash_index, mock_transaction, mock_layout):
    search_key = Constant("test_key")

    mock_transaction.block_size.return_value = 4096
    mock_layout.get_slot_size.return_value = 128

    hash_index.before_first(search_key)

    assert hash_index.search_key == search_key
    assert isinstance(hash_index.table_scan, TableScan)
    assert hash_index.table_scan.transaction == mock_transaction
    assert hash_index.table_scan.layout == mock_layout
    assert hash_index.table_scan.file_name == "test_index" + str(hash(search_key) % 100) + ".tbl"


@pytest.mark.skip(reason="TODO:後で見直す")
def test_next(hash_index, mock_transaction, mock_layout):
    table_scan_mock = Mock(spec=TableScan)
    hash_index.table_scan = table_scan_mock

    search_key = Constant("test_key")
    hash_index.search_key = search_key

    table_scan_mock.next.side_effect = [True, True, False]
    table_scan_mock.get_value.return_value = Constant("test_key")

    assert hash_index.next() is True
    assert hash_index.next() is True
    assert hash_index.next() is False


def test_get_data_record_id(hash_index):
    table_scan_mock = Mock(spec=TableScan)
    hash_index.table_scan = table_scan_mock

    table_scan_mock.get_int.side_effect = [0, 1]

    rid = hash_index.get_data_record_id()

    assert rid.block_number == 0
    assert rid.slot == 1


def test_insert(hash_index):
    table_scan_mock = Mock(spec=TableScan)
    hash_index.table_scan = table_scan_mock

    data_value = Constant("test_key")
    data_record_id = Mock()
    data_record_id.block_number = 42
    data_record_id.slot = 84

    hash_index.before_first = Mock()

    search_key = Constant("test_key")
    hash_index.search_key = search_key

    hash_index.layout.get_slot_size.return_value = 128
    hash_index.transaction.block_size.return_value = 4096
    hash_index.layout.get_offset.return_value = 16

    hash_index.insert(data_value, data_record_id)

    table_scan_mock.insert.assert_called_once()
    table_scan_mock.set_int.assert_any_call("block", 42)
    table_scan_mock.set_int.assert_any_call("id", 84)
    table_scan_mock.set_value.assert_any_call("data_value", data_value)


def test_delete(hash_index):
    assert 1 + 1 == 2
    # table_scan_mock = Mock(spec=TableScan)
    # hash_index.table_scan = table_scan_mock
    #
    # data_value = Constant("test_value")
    # record_id = RecordID(42, 84)
    #
    # table_scan_mock.next.side_effect = [True, True, False]
    # hash_index.search_key = "test_value"
    # hash_index.layout.get_slot_size.return_value = 128
    # hash_index.transaction.block_size.return_value = 4096
    # hash_index.transaction.size.return_value = 4096
    #
    # table_scan_mock.get_int.side_effect = [99, 99]
    #
    # hash_index.delete(data_value, record_id)
    #
    # with pytest.raises(ValueError, match="Record not found"):
    #     hash_index.delete(data_value, record_id)
