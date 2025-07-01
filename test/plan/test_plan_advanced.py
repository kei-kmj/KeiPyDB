"""
Advanced tests for db/plan module to discover more production issues
"""

import pytest
from unittest.mock import Mock

# Import plan module classes
from db.plan.table_plan import TablePlan
from db.plan.product_plan import ProductPlan
from db.plan.select_plan import SelectPlan
from db.plan.project_plan import ProjectPlan
from db.plan.basic_query_planner import BasicQueryPlanner
from db.plan.better_query_planner import BetterQueryPlanner

# Import dependencies
from db.record.schema import Schema
from db.constants import FieldType
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.term import Term
from db.query.predicate import Predicate
from db.parse.query_data import QueryData


def test_product_plan_field_resolution_issues():
    """Test ProductPlan field resolution and potential conflicts"""
    
    # Create plans with overlapping field names
    left_plan = Mock()
    left_schema = Schema()
    left_schema.add_field("id", FieldType.Integer, 0)  # Overlapping field
    left_schema.add_field("name", FieldType.Varchar, 50)
    left_plan.schema.return_value = left_schema
    left_plan.blocks_accessed.return_value = 10
    left_plan.records_output.return_value = 100
    left_plan.distinct_values.return_value = 50
    
    right_plan = Mock()
    right_schema = Schema()
    right_schema.add_field("id", FieldType.Integer, 0)  # Overlapping field
    right_schema.add_field("course_name", FieldType.Varchar, 30)
    right_plan.schema.return_value = right_schema
    right_plan.blocks_accessed.return_value = 5
    right_plan.records_output.return_value = 200
    right_plan.distinct_values.return_value = 25
    
    product_plan = ProductPlan(left_plan, right_plan)
    
    # Test schema combination with duplicate fields
    combined_schema = product_plan.schema()
    field_count = {}
    for field in combined_schema.fields:
        field_count[field] = field_count.get(field, 0) + 1
    
    print(f"Field count in combined schema: {field_count}")
    
    # ISSUE: ProductPlan might create duplicate fields
    if field_count.get("id", 0) > 1:
        print("WARNING: Duplicate 'id' field detected in ProductPlan schema")
    
    # Test distinct values with overlapping field names
    left_distinct = product_plan.distinct_values("id")
    print(f"Distinct values for 'id' field: {left_distinct}")
    
    # Test which schema takes precedence for overlapping fields
    try:
        # This should test the field resolution logic
        combined_schema.has_field("id")
        print("Field resolution works for overlapping names")
    except Exception as e:
        print(f"Field resolution error: {e}")


def test_select_plan_predicate_optimization_issues():
    """Test SelectPlan predicate optimization edge cases"""
    
    base_plan = Mock()
    base_plan.blocks_accessed.return_value = 100
    base_plan.records_output.return_value = 1000
    base_plan.distinct_values.return_value = 500
    
    schema = Schema()
    schema.add_field("age", FieldType.Integer, 0)
    schema.add_field("status", FieldType.Varchar, 20)
    base_plan.schema.return_value = schema
    
    # Test 1: Predicate with constant that should optimize distinct values
    predicate1 = Predicate()
    age_term = Term(Expression("age"), Expression(Constant(25)))
    predicate1.add_term(age_term)
    
    select_plan1 = SelectPlan(base_plan, predicate1)
    
    # Check if distinct_values is optimized for constant predicates
    age_distinct = select_plan1.distinct_values("age")
    status_distinct = select_plan1.distinct_values("status")
    
    print(f"Age distinct (with constant predicate): {age_distinct}")
    print(f"Status distinct (no constant predicate): {status_distinct}")
    
    # Test predicate constant detection
    age_constant = predicate1.equates_with_constant("age")
    print(f"Age constant from predicate: {age_constant}")
    
    # ISSUE FOUND: equates_with_constant may not work correctly
    # Expected: age_distinct should be 1 (optimized)
    # Expected: age_constant should return Constant(25)
    
    # Test 2: Field-to-field predicate
    predicate2 = Predicate()
    field_term = Term(Expression("age"), Expression("status"))  # Invalid comparison
    predicate2.add_term(field_term)
    
    select_plan2 = SelectPlan(base_plan, predicate2)
    
    # This should not optimize distinct values
    age_distinct2 = select_plan2.distinct_values("age")
    print(f"Age distinct (with field predicate): {age_distinct2}")
    
    # Test 3: Multiple predicates
    predicate3 = Predicate()
    predicate3.add_term(age_term)
    status_term = Term(Expression("status"), Expression(Constant("active")))
    predicate3.add_term(status_term)
    
    select_plan3 = SelectPlan(base_plan, predicate3)
    
    age_constant3 = predicate3.equates_with_constant("age")
    status_constant3 = predicate3.equates_with_constant("status")
    
    print(f"Multi-predicate age constant: {age_constant3}")
    print(f"Multi-predicate status constant: {status_constant3}")


def test_project_plan_schema_field_validation():
    """Test ProjectPlan with invalid field names"""
    
    base_plan = Mock()
    base_plan.blocks_accessed.return_value = 50
    base_plan.records_output.return_value = 200
    base_plan.distinct_values.return_value = 100
    
    base_schema = Schema()
    base_schema.add_field("id", FieldType.Integer, 0)
    base_schema.add_field("name", FieldType.Varchar, 50)
    base_schema.add_field("age", FieldType.Integer, 0)
    base_plan.schema.return_value = base_schema
    
    # Test with valid fields
    valid_fields = ["name", "age"]
    project_plan1 = ProjectPlan(base_plan, valid_fields)
    valid_schema = project_plan1.schema()
    
    assert len(valid_schema.fields) == 2
    assert "name" in valid_schema.fields
    assert "age" in valid_schema.fields
    
    # Test with invalid field names
    invalid_fields = ["nonexistent_field", "another_missing_field"]
    project_plan2 = ProjectPlan(base_plan, invalid_fields)
    
    # ProjectPlan should create schema even with invalid fields
    invalid_schema = project_plan2.schema()
    print(f"Schema with invalid fields: {invalid_schema.fields}")
    
    # ISSUE: ProjectPlan might create schema with fields that don't exist in base
    # This could cause runtime errors later
    
    # Test mixed valid/invalid fields
    mixed_fields = ["name", "nonexistent_field", "age"]
    project_plan3 = ProjectPlan(base_plan, mixed_fields)
    mixed_schema = project_plan3.schema()
    
    print(f"Schema with mixed fields: {mixed_schema.fields}")
    
    # Test distinct values with invalid fields
    try:
        distinct_invalid = project_plan2.distinct_values("nonexistent_field")
        print(f"Distinct values for invalid field: {distinct_invalid}")
    except Exception as e:
        print(f"Error getting distinct values for invalid field: {e}")


def test_query_planner_edge_cases():
    """Test query planners with edge cases"""
    
    # Setup mock metadata manager
    mock_metadata = Mock()
    
    # Test 1: Empty table list
    empty_query = QueryData([], ["field1"])
    empty_predicate = Predicate()
    empty_query.pred = empty_predicate
    
    basic_planner = BasicQueryPlanner(mock_metadata)
    
    try:
        empty_plan = basic_planner.create_plan(empty_query, Mock())
        print(f"Empty table plan: {empty_plan}")
    except Exception as e:
        print(f"Error with empty table list: {e}")
    
    # Test 2: Single table query
    mock_layout = Mock()
    mock_schema = Schema()
    mock_schema.add_field("field1", FieldType.Integer, 0)
    mock_layout.schema = mock_schema
    mock_metadata.get_layout.return_value = mock_layout
    
    mock_stat_info = Mock()
    mock_stat_info.blocks_accessed.return_value = 10
    mock_stat_info.records_output.return_value = 100
    mock_stat_info.distinct_values.return_value = 50
    mock_metadata.get_stat_info.return_value = mock_stat_info
    
    single_query = QueryData(["table1"], ["field1"])
    single_predicate = Predicate()
    single_query.pred = single_predicate
    
    try:
        single_plan = basic_planner.create_plan(single_query, Mock())
        print(f"Single table plan created successfully")
        
        # Test plan properties
        print(f"Plan blocks: {single_plan.blocks_accessed()}")
        print(f"Plan records: {single_plan.records_output()}")
        
    except Exception as e:
        print(f"Error with single table query: {e}")
    
    # Test 3: Multiple tables with no join predicates
    multi_query = QueryData(["table1", "table2"], ["field1"])
    multi_predicate = Predicate()
    multi_query.pred = multi_predicate
    
    try:
        multi_plan = basic_planner.create_plan(multi_query, Mock())
        print(f"Multi-table plan created")
        
        # This should create a Cartesian product
        print(f"Multi-table plan blocks: {multi_plan.blocks_accessed()}")
        print(f"Multi-table plan records: {multi_plan.records_output()}")
        
    except Exception as e:
        print(f"Error with multi-table query: {e}")


def test_better_query_planner_optimization():
    """Test BetterQueryPlanner optimization logic"""
    
    mock_metadata = Mock()
    
    # Setup two tables with different costs
    def mock_get_layout(table_name):
        schema = Schema()
        if table_name == "small_table":
            schema.add_field("id", FieldType.Integer, 0)
        else:  # large_table
            schema.add_field("id", FieldType.Integer, 0)
            schema.add_field("data", FieldType.Varchar, 100)
        
        layout = Mock()
        layout.schema = schema
        return layout
    
    def mock_get_stat_info(table_name, tx):
        stat_info = Mock()
        if table_name == "small_table":
            stat_info.blocks_accessed.return_value = 5
            stat_info.records_output.return_value = 100
            stat_info.distinct_values.return_value = 50
        else:  # large_table
            stat_info.blocks_accessed.return_value = 50
            stat_info.records_output.return_value = 10000
            stat_info.distinct_values.return_value = 5000
        return stat_info
    
    mock_metadata.get_layout.side_effect = mock_get_layout
    mock_metadata.get_stat_info.side_effect = mock_get_stat_info
    
    better_planner = BetterQueryPlanner(mock_metadata)
    
    # Create query with two tables
    optimization_query = QueryData(["small_table", "large_table"], ["id"])
    join_predicate = Predicate()
    optimization_query.pred = join_predicate
    
    try:
        optimized_plan = better_planner.create_plan(optimization_query, Mock())
        print(f"Optimized plan created")
        
        # Test optimization results
        optimized_cost = optimized_plan.blocks_accessed()
        print(f"Optimized plan cost: {optimized_cost}")
        
        # Compare with basic planner
        basic_planner = BasicQueryPlanner(mock_metadata)
        basic_plan = basic_planner.create_plan(optimization_query, Mock())
        basic_cost = basic_plan.blocks_accessed()
        
        print(f"Basic plan cost: {basic_cost}")
        print(f"Optimization improvement: {basic_cost - optimized_cost}")
        
    except Exception as e:
        print(f"Error in optimization test: {e}")


def test_plan_statistics_consistency():
    """Test that plan statistics are calculated consistently"""
    
    # Create base plans with known statistics
    plan1 = Mock()
    plan1.blocks_accessed.return_value = 10
    plan1.records_output.return_value = 100
    plan1.distinct_values.return_value = 50
    
    schema1 = Schema()
    schema1.add_field("field1", FieldType.Integer, 0)
    plan1.schema.return_value = schema1
    
    plan2 = Mock()
    plan2.blocks_accessed.return_value = 20
    plan2.records_output.return_value = 200
    plan2.distinct_values.return_value = 100
    
    schema2 = Schema()
    schema2.add_field("field2", FieldType.Integer, 0)
    plan2.schema.return_value = schema2
    
    # Test ProductPlan statistics
    product_plan = ProductPlan(plan1, plan2)
    
    # Verify cost formula: left.blocks + (right.records * left.blocks)
    expected_blocks = 10 + (200 * 10)  # 10 + 2000 = 2010
    expected_records = 100 * 200       # 20000
    
    assert product_plan.blocks_accessed() == expected_blocks
    assert product_plan.records_output() == expected_records
    
    print(f"ProductPlan statistics verified: {expected_blocks} blocks, {expected_records} records")
    
    # Test distinct values for different fields
    distinct1 = product_plan.distinct_values("field1")
    distinct2 = product_plan.distinct_values("field2")
    
    print(f"ProductPlan distinct values - field1: {distinct1}, field2: {distinct2}")
    
    # Test SelectPlan statistics
    predicate = Predicate()
    select_plan = SelectPlan(plan1, predicate)
    
    # SelectPlan should pass through base statistics
    assert select_plan.blocks_accessed() == 10
    assert select_plan.records_output() == 100
    
    # Test ProjectPlan statistics
    project_plan = ProjectPlan(plan1, ["field1"])
    
    # ProjectPlan should pass through base statistics
    assert project_plan.blocks_accessed() == 10
    assert project_plan.records_output() == 100
    assert project_plan.distinct_values("field1") == 50
    
    print("Plan statistics consistency verified")


def test_error_propagation():
    """Test error handling and propagation in plans"""
    
    # Test with mock that raises exceptions
    error_plan = Mock()
    error_plan.blocks_accessed.side_effect = RuntimeError("Statistics unavailable")
    error_plan.records_output.return_value = 100
    error_plan.schema.return_value = Schema()
    
    # Test ProductPlan error handling
    normal_plan = Mock()
    normal_plan.blocks_accessed.return_value = 10
    normal_plan.records_output.return_value = 50
    normal_plan.schema.return_value = Schema()
    
    try:
        product_with_error = ProductPlan(error_plan, normal_plan)
        cost = product_with_error.blocks_accessed()
        print(f"Unexpected success with error plan: {cost}")
    except RuntimeError as e:
        print(f"Expected error propagated: {e}")
    
    # Test SelectPlan with problematic predicate
    problematic_predicate = Mock()
    problematic_predicate.equates_with_constant.side_effect = AttributeError("Method not found")
    
    try:
        select_with_error = SelectPlan(normal_plan, problematic_predicate)
        distinct = select_with_error.distinct_values("field1")
        print(f"SelectPlan handled predicate error gracefully: {distinct}")
    except AttributeError as e:
        print(f"Predicate error propagated: {e}")


if __name__ == "__main__":
    test_product_plan_field_resolution_issues()
    test_select_plan_predicate_optimization_issues()
    test_project_plan_schema_field_validation()
    test_query_planner_edge_cases()
    test_better_query_planner_optimization()
    test_plan_statistics_consistency()
    test_error_propagation()
    print("All advanced plan tests completed!")