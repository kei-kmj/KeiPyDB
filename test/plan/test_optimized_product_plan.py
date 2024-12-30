from unittest.mock import Mock

import pytest

from db.plan.optimized_product_plan import OptimizedProductPlan
from db.plan.plan import Plan
from db.query.product_scan import ProductScan
from db.query.scan import Scan
from db.record.schema import Schema


@pytest.fixture
def mock_plan_first():
    plan = Mock(spec=Plan)
    schema_mock = Mock(spec=Schema)
    schema_mock.get_fields.return_value = ["field1", "field2"]
    plan.schema.return_value = schema_mock
    plan.block_accessed.return_value = 100
    plan.record_output.return_value = 200
    plan.distinct_values.return_value = 10
    plan.open.return_value = Mock(spec=Scan)
    return plan


@pytest.fixture
def mock_plan_second():
    plan = Mock(spec=Plan)
    schema_mock = Mock(spec=Schema)
    schema_mock.get_fields.return_value = ["field3", "field4"]
    plan.schema.return_value = schema_mock
    plan.block_accessed.return_value = 150
    plan.record_output.return_value = 300
    plan.distinct_values.return_value = 20
    plan.open.return_value = Mock(spec=Scan)
    return plan


@pytest.fixture
def optimized_product_plan(mock_plan_first, mock_plan_second):
    return OptimizedProductPlan(mock_plan_first, mock_plan_second)


def test_openメソッドが最適なプランを開くこと(mock_plan_first, mock_plan_second, optimized_product_plan):
    scan = optimized_product_plan.open()
    assert isinstance(scan, ProductScan)


def test_block_accessedメソッドが最適な値を返すこと(mock_plan_first, mock_plan_second, optimized_product_plan):
    expected_value = mock_plan_first.block_accessed() + (
        mock_plan_second.record_output() * mock_plan_first.block_accessed()
    )
    assert optimized_product_plan.block_accessed() == expected_value


def test_record_outputメソッドが最適な値を返すこと(mock_plan_first, mock_plan_second, optimized_product_plan):
    assert optimized_product_plan.record_output() == mock_plan_first.record_output() * mock_plan_second.record_output()


def test_distinct_valuesメソッドが正しい値を返すこと(mock_plan_first, mock_plan_second, optimized_product_plan):
    mock_plan_first.schema.return_value.has_field.return_value = True
    assert optimized_product_plan.distinct_values("field1") == 10
    mock_plan_first.distinct_values.assert_called_once_with("field1")


def test_schemaメソッドが正しいスキーマを返すこと(mock_plan_first, mock_plan_second, optimized_product_plan):
    schema = optimized_product_plan.schema()
    assert isinstance(schema, Schema)
    mock_plan_first.schema.assert_any_call()
    mock_plan_second.schema.assert_any_call()
