from unittest.mock import Mock

import pytest

from db.metadata.metadata_manager import MetadataManager
from db.metadata.stat_info import StatInfo
from db.plan.table_plan import TablePlan
from db.record.layout import Layout
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


@pytest.fixture
def mock_metadata_manager():
    metadata_manager = Mock(spec=MetadataManager)
    metadata_manager.get_layout.return_value = Mock(spec=Layout)
    metadata_manager.get_stat_info.return_value = Mock(spec=StatInfo)
    return metadata_manager


@pytest.fixture
def mock_transaction():
    return Mock(spec=Transaction)


@pytest.fixture
def table_plan(mock_transaction, mock_metadata_manager):
    return TablePlan(mock_transaction, "test_table", mock_metadata_manager)


def test_openメソッドが正しいスキャンを返すこと(mock_transaction, mock_metadata_manager, table_plan):

    scan = table_plan.open()

    assert isinstance(scan, TableScan)


def test_block_accessedメソッドが正しい値を返すこと(mock_transaction, mock_metadata_manager, table_plan):
    stat_info = mock_metadata_manager.get_stat_info.return_value
    stat_info.blocks_accessed.return_value = 100

    assert table_plan.blocks_accessed() == 100


def test_record_outputメソッドが正しい値を返すこと(mock_transaction, mock_metadata_manager, table_plan):
    stat_info = mock_metadata_manager.get_stat_info.return_value
    stat_info.records_output.return_value = 200

    assert table_plan.records_output() == 200


def test_distinct_valuesメソッドが正しい値を返すこと(mock_transaction, mock_metadata_manager, table_plan):
    stat_info = mock_metadata_manager.get_stat_info.return_value
    stat_info.distinct_values.return_value = 300

    assert table_plan.distinct_values("test_field") == 300


def test_schemaメソッドが正しい値を返すこと(mock_transaction, mock_metadata_manager, table_plan):
    layout = mock_metadata_manager.get_layout.return_value
    schema = Mock(spec=Schema)
    layout.schema = schema

    assert table_plan.schema() == schema
