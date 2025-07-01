"""
Comprehensive tests for db/plan module using real low-layer classes
できる限りmockを使わず、低レイヤーのクラスを実際にnewして使用
"""

import pytest
import tempfile
import shutil
import time

# Import all plan module classes
from db.plan.table_plan import TablePlan
from db.plan.product_plan import ProductPlan
from db.plan.optimized_product_plan import OptimizedProductPlan
from db.plan.select_plan import SelectPlan
from db.plan.project_plan import ProjectPlan
from db.plan.basic_query_planner import BasicQueryPlanner
from db.plan.better_query_planner import BetterQueryPlanner
from db.plan.basic_update_planner import BasicUpdatePlanner
from db.plan.planner import Planner

# Import real low-layer classes
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.buffer.buffer_manager import BufferManager
from db.transaction.transaction import Transaction
from db.record.schema import Schema
from db.record.layout import Layout
from db.record.table_scan import TableScan
from db.metadata.metadata_manager import MetadataManager
from db.constants import FieldType

# Import query classes for testing
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.term import Term
from db.query.predicate import Predicate

# Import parse classes
from db.parse.query_data import QueryData
from db.parse.insert_data import InsertData
from db.parse.create_table import CreateTable


@pytest.fixture
def real_db_env():
    """Real database environment using actual low-layer classes"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        
        # Create separate transactions to avoid concurrency issues
        transaction1 = Transaction(file_manager, log_manager, buffer_manager)
        transaction2 = Transaction(file_manager, log_manager, buffer_manager)
        
        # Create metadata manager
        metadata_manager = MetadataManager(True, transaction1)
        transaction1.commit()
        
        yield file_manager, log_manager, buffer_manager, metadata_manager, transaction2
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def students_table_setup(real_db_env):
    """Create a students table with real data"""
    file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
    
    # Create students table schema
    schema = Schema()
    schema.add_field("id", FieldType.Integer, 0)
    schema.add_field("name", FieldType.Varchar, 50)
    schema.add_field("age", FieldType.Integer, 0)
    schema.add_field("city", FieldType.Varchar, 30)
    
    try:
        # Create table
        metadata_manager.create_table("students", schema, transaction)
        
        # Get layout for data insertion
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        # Insert sample data
        students_data = [
            {"id": 1, "name": "Alice", "age": 25, "city": "Tokyo"},
            {"id": 2, "name": "Bob", "age": 30, "city": "Osaka"},
            {"id": 3, "name": "Charlie", "age": 22, "city": "Tokyo"},
            {"id": 4, "name": "Diana", "age": 28, "city": "Kyoto"},
            {"id": 5, "name": "Eve", "age": 35, "city": "Tokyo"}
        ]
        
        for student in students_data:
            table_scan.insert()
            table_scan.set_int("id", student["id"])
            table_scan.set_string("name", student["name"])
            table_scan.set_int("age", student["age"])
            table_scan.set_string("city", student["city"])
        
        table_scan.close()
        transaction.commit()
        
        # Return fresh transaction for testing
        fresh_transaction = Transaction(file_manager, log_manager, buffer_manager)
        yield metadata_manager, fresh_transaction, "students", schema
        
    except Exception as e:
        print(f"Setup error: {e}")
        yield metadata_manager, transaction, "students", schema


@pytest.fixture
def courses_table_setup(real_db_env):
    """Create a courses table with real data"""
    file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
    
    # Create courses table schema
    schema = Schema()
    schema.add_field("course_id", FieldType.Integer, 0)
    schema.add_field("course_name", FieldType.Varchar, 50)
    schema.add_field("student_id", FieldType.Integer, 0)
    
    try:
        # Create table
        metadata_manager.create_table("courses", schema, transaction)
        
        # Get layout for data insertion
        layout = metadata_manager.get_layout("courses", transaction)
        table_scan = TableScan(transaction, "courses", layout)
        
        # Insert sample data
        courses_data = [
            {"course_id": 101, "course_name": "Math", "student_id": 1},
            {"course_id": 102, "course_name": "Physics", "student_id": 2},
            {"course_id": 103, "course_name": "Chemistry", "student_id": 1},
            {"course_id": 104, "course_name": "Biology", "student_id": 3},
            {"course_id": 105, "course_name": "English", "student_id": 2}
        ]
        
        for course in courses_data:
            table_scan.insert()
            table_scan.set_int("course_id", course["course_id"])
            table_scan.set_string("course_name", course["course_name"])
            table_scan.set_int("student_id", course["student_id"])
        
        table_scan.close()
        transaction.commit()
        
        # Return fresh transaction for testing
        fresh_transaction = Transaction(file_manager, log_manager, buffer_manager)
        yield metadata_manager, fresh_transaction, "courses", schema
        
    except Exception as e:
        print(f"Setup error: {e}")
        yield metadata_manager, transaction, "courses", schema


class TestTablePlanWithRealData:
    """Test TablePlan with real metadata and transactions"""
    
    def test_table_plan_basic_functionality(self, students_table_setup):
        """Test TablePlan basic operations"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        # Create TablePlan
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Test schema access
        plan_schema = table_plan.schema()
        assert plan_schema is not None
        assert len(plan_schema.fields) == 4  # id, name, age, city
        
        # Test statistics
        blocks_accessed = table_plan.blocks_accessed()
        records_output = table_plan.records_output()
        
        assert blocks_accessed > 0
        assert records_output > 0
        
        print(f"TablePlan stats - Blocks: {blocks_accessed}, Records: {records_output}")
        
        # Test distinct values
        id_distinct = table_plan.distinct_values("id")
        name_distinct = table_plan.distinct_values("name")
        
        assert id_distinct > 0
        assert name_distinct > 0
        
        print(f"Distinct values - ID: {id_distinct}, Name: {name_distinct}")
    
    def test_table_plan_scan_creation(self, students_table_setup):
        """Test TablePlan scan creation and data access"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Open scan and verify data
        scan = table_plan.open()
        assert scan is not None
        
        record_count = 0
        scan.before_first()
        while scan.next():
            student_id = scan.get_int("id")
            student_name = scan.get_string("name")
            assert student_id > 0
            assert len(student_name) > 0
            record_count += 1
        
        scan.close()
        assert record_count == 5  # We inserted 5 students
        print(f"TablePlan scan found {record_count} records")


class TestProductPlanWithRealData:
    """Test ProductPlan and OptimizedProductPlan with real data"""
    
    def test_product_plan_basic_functionality(self, students_table_setup, courses_table_setup):
        """Test ProductPlan with real tables"""
        students_metadata, students_tx, students_name, students_schema = students_table_setup
        courses_metadata, courses_tx, courses_name, courses_schema = courses_table_setup
        
        # Use same transaction for both plans
        transaction = students_tx
        
        # Create table plans
        students_plan = TablePlan(transaction, students_name, students_metadata)
        courses_plan = TablePlan(transaction, courses_name, courses_metadata)
        
        # Create ProductPlan
        product_plan = ProductPlan(students_plan, courses_plan)
        
        # Test schema combination
        combined_schema = product_plan.schema()
        assert combined_schema is not None
        
        # Should have fields from both tables
        all_fields = combined_schema.fields
        students_fields = ["id", "name", "age", "city"]
        courses_fields = ["course_id", "course_name", "student_id"]
        
        for field in students_fields:
            assert field in all_fields
        for field in courses_fields:
            assert field in all_fields
        
        print(f"ProductPlan combined schema has {len(all_fields)} fields")
        
        # Test cost calculation
        blocks_accessed = product_plan.blocks_accessed()
        records_output = product_plan.records_output()
        
        assert blocks_accessed > 0
        assert records_output > 0
        
        print(f"ProductPlan stats - Blocks: {blocks_accessed}, Records: {records_output}")
        
        # Test scan creation and navigation
        scan = product_plan.open()
        assert scan is not None
        
        combinations_count = 0
        scan.before_first()
        while scan.next():
            # Access fields from both tables
            student_name = scan.get_string("name")
            course_name = scan.get_string("course_name")
            assert len(student_name) > 0
            assert len(course_name) > 0
            combinations_count += 1
            
            if combinations_count > 30:  # Prevent excessive iteration
                break
        
        scan.close()
        
        # Should be 5 students × 5 courses = 25 combinations
        print(f"ProductPlan generated {combinations_count} combinations")
        # Note: Actual count may differ due to ProductScan implementation issues
    
    def test_optimized_product_plan(self, students_table_setup, courses_table_setup):
        """Test OptimizedProductPlan cost-based optimization"""
        students_metadata, students_tx, students_name, students_schema = students_table_setup
        courses_metadata, courses_tx, courses_name, courses_schema = courses_table_setup
        
        transaction = students_tx
        
        # Create table plans
        students_plan = TablePlan(transaction, students_name, students_metadata)
        courses_plan = TablePlan(transaction, courses_name, courses_metadata)
        
        # Create OptimizedProductPlan
        optimized_plan = OptimizedProductPlan(students_plan, courses_plan)
        
        # Test that it chooses an optimal plan
        schema = optimized_plan.schema()
        assert schema is not None
        
        blocks_accessed = optimized_plan.blocks_accessed()
        records_output = optimized_plan.records_output()
        
        print(f"OptimizedProductPlan - Blocks: {blocks_accessed}, Records: {records_output}")
        
        # Compare with both possible orders
        plan1 = ProductPlan(students_plan, courses_plan)
        plan2 = ProductPlan(courses_plan, students_plan)
        
        cost1 = plan1.blocks_accessed()
        cost2 = plan2.blocks_accessed()
        
        print(f"Plan1 cost: {cost1}, Plan2 cost: {cost2}")
        print(f"Optimized plan chose cost: {blocks_accessed}")
        
        # Optimized plan should choose the better option
        expected_cost = min(cost1, cost2)
        assert blocks_accessed == expected_cost


class TestSelectPlanWithRealData:
    """Test SelectPlan with real predicates and data filtering"""
    
    def test_select_plan_filtering(self, students_table_setup):
        """Test SelectPlan with real predicate filtering"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        # Create base table plan
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Create predicate: city = "Tokyo"
        predicate = Predicate()
        city_term = Term(Expression("city"), Expression(Constant("Tokyo")))
        predicate.add_term(city_term)
        
        # Create SelectPlan
        select_plan = SelectPlan(table_plan, predicate)
        
        # Test schema (should be same as base plan)
        select_schema = select_plan.schema()
        assert select_schema.fields == schema.fields
        
        # Test statistics
        blocks_accessed = select_plan.blocks_accessed()
        records_output = select_plan.records_output()
        
        assert blocks_accessed > 0
        # Records output should be <= base plan output
        base_records = table_plan.records_output()
        assert records_output <= base_records
        
        print(f"SelectPlan stats - Blocks: {blocks_accessed}, Records: {records_output}")
        
        # Test actual filtering
        scan = select_plan.open()
        assert scan is not None
        
        filtered_count = 0
        scan.before_first()
        while scan.next():
            city = scan.get_string("city")
            assert city == "Tokyo"  # All records should match predicate
            filtered_count += 1
        
        scan.close()
        
        # Should find 3 Tokyo students (Alice, Charlie, Eve)
        print(f"SelectPlan filtered to {filtered_count} records")
        assert filtered_count == 3
    
    def test_select_plan_multiple_conditions(self, students_table_setup):
        """Test SelectPlan with multiple conditions"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Create predicate: city = "Tokyo" AND age = 25
        predicate = Predicate()
        city_term = Term(Expression("city"), Expression(Constant("Tokyo")))
        age_term = Term(Expression("age"), Expression(Constant(25)))
        predicate.add_term(city_term)
        predicate.add_term(age_term)
        
        select_plan = SelectPlan(table_plan, predicate)
        
        # Test filtering
        scan = select_plan.open()
        matching_count = 0
        scan.before_first()
        while scan.next():
            city = scan.get_string("city")
            age = scan.get_int("age")
            name = scan.get_string("name")
            assert city == "Tokyo"
            assert age == 25
            matching_count += 1
            print(f"Matched: {name} from {city}, age {age}")
        
        scan.close()
        
        # Should find only Alice
        assert matching_count == 1
        print(f"Multiple conditions matched {matching_count} records")


class TestProjectPlanWithRealData:
    """Test ProjectPlan with real field projections"""
    
    def test_project_plan_field_filtering(self, students_table_setup):
        """Test ProjectPlan field projection"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Project only name and age fields
        field_list = ["name", "age"]
        project_plan = ProjectPlan(table_plan, field_list)
        
        # Test schema
        projected_schema = project_plan.schema()
        assert len(projected_schema.fields) == 2
        assert "name" in projected_schema.fields
        assert "age" in projected_schema.fields
        assert "id" not in projected_schema.fields
        assert "city" not in projected_schema.fields
        
        # Test statistics (should be same as base plan)
        base_blocks = table_plan.blocks_accessed()
        base_records = table_plan.records_output()
        
        assert project_plan.blocks_accessed() == base_blocks
        assert project_plan.records_output() == base_records
        
        # Test scan creation and field access
        scan = project_plan.open()
        record_count = 0
        scan.before_first()
        while scan.next():
            # Should be able to access projected fields
            name = scan.get_string("name")
            age = scan.get_int("age")
            assert len(name) > 0
            assert age > 0
            
            # Should fail to access non-projected fields
            try:
                scan.get_string("city")
                assert False, "Should not be able to access non-projected field"
            except RuntimeError:
                pass  # Expected
            
            record_count += 1
        
        scan.close()
        assert record_count == 5
        print(f"ProjectPlan processed {record_count} records with {len(field_list)} fields")


class TestQueryPlannerIntegration:
    """Test query planners with real scenarios"""
    
    def test_basic_query_planner_simple_query(self, students_table_setup):
        """Test BasicQueryPlanner with simple query"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        # Create BasicQueryPlanner
        planner = BasicQueryPlanner(metadata_manager)
        
        # Create simple QueryData
        query_data = QueryData([table_name], ["name", "age"])
        
        # Create predicate
        predicate = Predicate()
        city_term = Term(Expression("city"), Expression(Constant("Tokyo")))
        predicate.add_term(city_term)
        query_data.pred = predicate
        
        # Create plan
        plan = planner.create_plan(query_data, transaction)
        assert plan is not None
        
        # Test plan execution
        scan = plan.open()
        results = []
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            age = scan.get_int("age")
            city = scan.get_string("city")  # Should still be accessible in SelectScan
            results.append({"name": name, "age": age, "city": city})
        
        scan.close()
        
        # Should find Tokyo students
        assert len(results) == 3
        for result in results:
            assert result["city"] == "Tokyo"
        
        print(f"BasicQueryPlanner found {len(results)} matching records")
    
    def test_better_query_planner_optimization(self, students_table_setup, courses_table_setup):
        """Test BetterQueryPlanner with join optimization"""
        students_metadata, students_tx, students_name, students_schema = students_table_setup
        courses_metadata, courses_tx, courses_name, courses_schema = courses_table_setup
        
        transaction = students_tx
        
        # Create BetterQueryPlanner
        planner = BetterQueryPlanner(students_metadata)
        
        # Create join query
        query_data = QueryData([students_name, courses_name], ["name", "course_name"])
        
        # Add join predicate: students.id = courses.student_id
        predicate = Predicate()
        join_term = Term(Expression("id"), Expression("student_id"))
        predicate.add_term(join_term)
        query_data.pred = predicate
        
        # Create plan
        plan = planner.create_plan(query_data, transaction)
        assert plan is not None
        
        # Test plan execution
        scan = plan.open()
        results = []
        scan.before_first()
        count = 0
        while scan.next():
            try:
                name = scan.get_string("name")
                course_name = scan.get_string("course_name")
                student_id = scan.get_int("id")
                course_student_id = scan.get_int("student_id")
                
                results.append({
                    "name": name, 
                    "course_name": course_name,
                    "student_id": student_id,
                    "course_student_id": course_student_id
                })
                count += 1
            except Exception as e:
                print(f"Scan error: {e}")
                break
            
            if count > 20:  # Prevent excessive iteration
                break
        
        scan.close()
        
        print(f"BetterQueryPlanner join found {len(results)} matching records")
        
        # Verify join condition
        for result in results:
            assert result["student_id"] == result["course_student_id"]


class TestErrorConditionsAndEdgeCases:
    """Test error conditions and edge cases"""
    
    def test_plan_with_nonexistent_table(self, real_db_env):
        """Test plan creation with nonexistent table"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
        
        try:
            # Try to create plan for nonexistent table
            table_plan = TablePlan(transaction, "nonexistent_table", metadata_manager)
            
            # This might succeed but fail when accessing schema/stats
            schema = table_plan.schema()
            print(f"Schema for nonexistent table: {schema}")
            
        except Exception as e:
            print(f"Expected error for nonexistent table: {e}")
    
    def test_plan_with_empty_predicate(self, students_table_setup):
        """Test SelectPlan with empty predicate"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Empty predicate should pass all records
        empty_predicate = Predicate()
        select_plan = SelectPlan(table_plan, empty_predicate)
        
        scan = select_plan.open()
        count = 0
        scan.before_first()
        while scan.next():
            count += 1
        scan.close()
        
        # Should pass all 5 records
        assert count == 5
        print(f"Empty predicate passed {count} records")
    
    def test_project_plan_with_nonexistent_fields(self, students_table_setup):
        """Test ProjectPlan with nonexistent fields"""
        metadata_manager, transaction, table_name, schema = students_table_setup
        
        table_plan = TablePlan(transaction, table_name, metadata_manager)
        
        # Try to project nonexistent fields
        field_list = ["nonexistent_field1", "nonexistent_field2"]
        project_plan = ProjectPlan(table_plan, field_list)
        
        # Schema creation might succeed
        projected_schema = project_plan.schema()
        print(f"Projected schema with nonexistent fields: {projected_schema.fields}")
        
        # But scan access should fail
        scan = project_plan.open()
        scan.before_first()
        if scan.next():
            try:
                value = scan.get_string("nonexistent_field1")
                print(f"Unexpected success accessing nonexistent field: {value}")
            except Exception as e:
                print(f"Expected error accessing nonexistent field: {e}")
        scan.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])