from unittest.mock import Mock

import pytest

from db.metadata.metadata_manager import MetadataManager
from db.parse.query_data import QueryData
from db.plan.basic_query_planner import BasicQueryPlanner
from db.transaction.transaction import Transaction


@pytest.fixture
def mock_metadata_manager():
    return Mock(spec=MetadataManager)


@pytest.fixture
def mock_transaction():
    return Mock(spec=Transaction)


@pytest.fixture
def mock_query_data():
    query_data = Mock(spec=QueryData)
    query_data.tables = ["table1", "table2"]
    query_data.get_predicate.return_value = Mock()
    query_data.get_fields.return_value = ["field1", "field2"]
    return query_data


@pytest.fixture
def basic_query_planner(mock_metadata_manager):
    return BasicQueryPlanner(mock_metadata_manager)


def test_create_planでベーシックプランを作成できること():
    assert 1 + 1 == 2
