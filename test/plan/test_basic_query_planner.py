import pytest
from unittest.mock import Mock, MagicMock
from db.plan.basic_query_planner import BasicQueryPlanner
from db.plan.table_plan import TablePlan
from db.plan.select_plan import SelectPlan
from db.plan.product_plan import ProductPlan
from db.plan.project_plan import ProjectPlan
from db.parse.query_data import QueryData
from db.metadata.metadata_manager import MetadataManager
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


def test_create_planでベーシックプランを作成できること(
        basic_query_planner, mock_query_data, mock_transaction, mock_metadata_manager
):
    mock_metadata_manager.get_view_definition.return_value = None

    # Execute the plan creation
    plan = basic_query_planner.create_plan(mock_query_data, mock_transaction)

    # Check the plan
    assert isinstance(plan, ProjectPlan)