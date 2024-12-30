import pytest
from unittest.mock import Mock
from db.plan.product_plan import ProductPlan
from db.plan.plan import Plan
from db.query.product_scan import ProductScan
from db.record.schema import Schema
from db.query.scan import Scan


@pytest.fixture
def mock_left_plan():
    left_plan = Mock(spec=Plan)
    schema_mock = Mock(spec=Schema)
    schema_mock.get_fields.return_value = ["field1", "field2"]
    left_plan.schema.return_value = schema_mock
    left_plan.block_accessed.return_value = 100
    left_plan.record_output.return_value = 200
    left_plan.distinct_values.return_value = 10
    left_plan.open.return_value = Mock(spec=Scan)
    return left_plan


@pytest.fixture
def mock_right_plan():
    right_plan = Mock(spec=Plan)
    schema_mock = Mock(spec=Schema)
    schema_mock.get_fields.return_value = ["field3", "field4"]
    right_plan.schema.return_value = schema_mock
    right_plan.block_accessed.return_value = 50
    right_plan.record_output.return_value = 300
    right_plan.distinct_values.return_value = 20
    right_plan.open.return_value = Mock(spec=Scan)
    return right_plan


@pytest.fixture
def product_plan(mock_left_plan, mock_right_plan):
    return ProductPlan(mock_left_plan, mock_right_plan)


def test_openメソッドが正しいスキャンを返すこと(mock_left_plan, mock_right_plan, product_plan):
    scan = product_plan.open()
    assert isinstance(scan, ProductScan)


def test_block_accessedメソッドが正しい値を返すこと(mock_left_plan, mock_right_plan, product_plan):
    expected_value = mock_left_plan.block_accessed() + (
        mock_right_plan.record_output() * mock_left_plan.block_accessed()
    )
    assert product_plan.block_accessed() == expected_value


def test_record_outputメソッドが正しい値を返すこと(mock_left_plan, mock_right_plan, product_plan):
    assert product_plan.record_output() == mock_left_plan.record_output() * mock_right_plan.record_output()


def test_distinct_valuesメソッドが左プランのフィールドで正しい値を返すこと(
    mock_left_plan, mock_right_plan, product_plan
):
    mock_left_plan.schema.return_value.has_field.return_value = True
    assert product_plan.distinct_values("field1") == 10
    mock_left_plan.distinct_values.assert_called_once_with("field1")
    mock_right_plan.distinct_values.assert_not_called()


def test_distinct_valuesメソッドが右プランのフィールドで正しい値を返すこと(
    mock_left_plan, mock_right_plan, product_plan
):
    mock_left_plan.schema.return_value.has_field.return_value = False
    mock_right_plan.distinct_values.return_value = 20
    assert product_plan.distinct_values("field_name") == mock_right_plan.distinct_values("field_name")
    mock_right_plan.distinct_values.assert_called_with("field_name")


def test_schemaメソッドが正しいスキーマを返すこと(mock_left_plan, mock_right_plan, product_plan):
    schema = product_plan.schema()
    assert isinstance(schema, Schema)
    assert schema.get_fields() == ["field1", "field2", "field3", "field4"]
    mock_left_plan.schema.assert_called_once()
    mock_right_plan.schema.assert_called_once()
