from unittest.mock import Mock, patch

from db.file.block_id import BlockID
from db.metadata.table_manager import TableManager
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


def test_テーブルレイアウトを取得できることを確認する():
    # Given
    transaction = Mock(spec=Transaction)
    transaction.block_size.return_value = 1024
    schema = Mock(spec=Schema)

    block_mock = Mock(spec=BlockID)
    block_mock.block_number.return_value = 0

    table_manager = TableManager(False, transaction)

    table_catalog_mock = Mock(spec=TableScan)
    field_catalog_mock = Mock(spec=TableScan)

    table_catalog_mock.next.side_effect = [True, False]
    table_catalog_mock.get_string.return_value = "test_table"
    table_catalog_mock.get_int.return_value = 128

    field_catalog_mock.next.side_effect = [True, True, False]
    field_catalog_mock.get_string.side_effect = ["test_table", "field1", "test_table", "field2"]
    field_catalog_mock.get_int.side_effect = [1, 10, 0, 2, 20, 128]

    with patch("db.record.table_scan.TableScan", side_effect=[table_catalog_mock, field_catalog_mock]):
        # When
        layout = table_manager.get_layout("test_table", transaction)

        # Then
        assert layout.get_slot_size() == 128
        assert layout.get_offset("field1") == 10
        assert layout.get_offset("field2") == 20
        assert schema.add_field.call_count == 2
        table_catalog_mock.close.assert_called_once()
        field_catalog_mock.close.assert_called_once()
