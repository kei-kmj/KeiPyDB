from unittest.mock import Mock

import pytest

from db.plan.plan import Plan
from db.plan.select_plan import SelectPlan
from db.query.predicate import Predicate
from db.query.select_scan import SelectScan
from db.record.schema import Schema


@pytest.fixture
def mock_plan():
    plan = Mock(spec=Plan)
    plan.block_accessed.return_value = 42
    plan.record_output.return_value = 100
    plan.distinct_values.return_value = 10
    plan.schema.return_value = Mock(spec=Schema)
    return plan


@pytest.fixture
def mock_predicate():
    predicate = Mock(spec=Predicate)
    predicate.equates_with_constant.return_value = None
    return predicate


@pytest.fixture
def select_plan(mock_plan, mock_predicate):
    return SelectPlan(mock_plan, mock_predicate)


def test_openメソッドが正しいスキャンを返すこと(mock_plan, mock_predicate, select_plan):
    scan = Mock()
    mock_plan.open.return_value = scan

    assert isinstance(select_plan.open(), SelectScan)
    assert select_plan.open().scan == scan
    assert select_plan.open().predicate == mock_predicate


def test_block_accessedメソッドが正しい値を返すこと(mock_plan, select_plan):

    assert select_plan.block_accessed() == 42
    mock_plan.block_accessed.assert_called_once()


def test_record_outputメソッドが正しい値を返すこと(mock_plan, select_plan):

    assert select_plan.record_output() == 100
    mock_plan.record_output.assert_called_once()


def test_distinct_valuesメソッドで条件に一致する場合(mock_plan, mock_predicate, select_plan):
    mock_predicate.equates_with_constant.return_value = 1

    assert select_plan.distinct_values("test_field") == 1
    mock_predicate.equates_with_constant.assert_called_once()


def test_distinct_valuesメソッドで条件が一致しない場合(mock_plan, mock_predicate, select_plan):
    assert select_plan.distinct_values("test_field") == 10
    mock_predicate.equates_with_constant.assert_called_once()
    mock_plan.distinct_values.assert_called_once()


def test_schemaメソッドが正しい値を返すこと(mock_plan, select_plan):

    assert select_plan.schema() == mock_plan.schema()
    mock_plan.schema.assert_any_call()
