from unittest.mock import Mock

import pytest

from db.plan.plan import Plan
from db.plan.project_plan import ProjectPlan
from db.query.project_scan import ProjectScan
from db.record.schema import Schema


@pytest.fixture
def mock_plan():
    plan = Mock(spec=Plan)
    plan.schema.return_value = Mock(spec=Schema)
    plan.blocks_accessed.return_value = 50
    plan.records_output.return_value = 100
    plan.distinct_values.return_value = 10
    return plan


@pytest.fixture
def field_list():
    return ["field1", "field2"]


@pytest.fixture
def project_plan(mock_plan, field_list):
    return ProjectPlan(mock_plan, field_list)


def test_open_scan(mock_plan, project_plan):
    scan = Mock()
    mock_plan.open.return_value = scan

    assert isinstance(project_plan.open(), ProjectScan)


def test_block_accessed_value(mock_plan, project_plan):
    assert project_plan.blocks_accessed() == 50
    mock_plan.blocks_accessed.assert_called_once()


def test_record_output_value(mock_plan, project_plan):
    assert project_plan.records_output() == 100
    mock_plan.records_output.assert_called_once()


def test_distinct_values_value(mock_plan, project_plan):
    assert project_plan.distinct_values("test_field") == 10
    mock_plan.distinct_values.assert_called_once_with("test_field")


def test_schema_schema(mock_plan, project_plan):
    schema = project_plan.schema()
    assert isinstance(schema, Schema)
    mock_plan.schema.assert_any_call()
