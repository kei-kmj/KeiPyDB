"""
Comprehensive tests for BasicUpdatePlanner using real low-layer classes
Tests DDL (CREATE TABLE, CREATE VIEW, CREATE INDEX) and DML (INSERT, UPDATE, DELETE) operations
Focuses on finding production code issues rather than just verifying functionality
"""

import pytest
import tempfile
import shutil

# Import the class under test
from db.plan.basic_update_planner import BasicUpdatePlanner

# Import real low-layer classes
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.buffer.buffer_manager import BufferManager
from db.transaction.transaction import Transaction
from db.metadata.metadata_manager import MetadataManager
from db.record.schema import Schema
from db.record.layout import Layout
from db.record.table_scan import TableScan
from db.constants import FieldType

# Import parse classes
from db.parse.insert_data import InsertData
from db.parse.delete_data import DeleteData
from db.parse.modify_data import ModifyData
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.create_index import CreateIndex
from db.parse.query_data import QueryData

# Import query classes
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.term import Term
from db.query.predicate import Predicate


@pytest.fixture
def real_db_env():
    """Real database environment using actual low-layer classes"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        
        # Create single transaction to avoid lock conflicts
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        # Create metadata manager
        metadata_manager = MetadataManager(True, transaction)
        transaction.commit()
        
        # Create fresh transaction for actual tests
        fresh_transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        yield file_manager, log_manager, buffer_manager, metadata_manager, fresh_transaction
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def update_planner_setup(real_db_env):
    """Create BasicUpdatePlanner with real dependencies"""
    file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
    
    planner = BasicUpdatePlanner(metadata_manager)
    
    yield planner, metadata_manager, transaction, file_manager, log_manager, buffer_manager


@pytest.fixture
def test_table_setup(update_planner_setup):
    """Create a test table for DML operations"""
    planner, metadata_manager, transaction, file_manager, log_manager, buffer_manager = update_planner_setup
    
    # Create students table schema
    schema = Schema()
    schema.add_field("id", FieldType.Integer, 0)
    schema.add_field("name", FieldType.Varchar, 50)
    schema.add_field("age", FieldType.Integer, 0)
    schema.add_field("gpa", FieldType.Varchar, 10)  # Using varchar to test string updates
    
    # Create table using planner
    create_table_data = CreateTable("students", schema)
    result = planner.execute_create_table(create_table_data, transaction)
    
    assert result == 0  # DDL operations should return 0
    
    yield planner, metadata_manager, transaction, "students", schema


class TestBasicUpdatePlannerDDL:
    """Test DDL operations (CREATE TABLE, CREATE VIEW, CREATE INDEX)"""
    
    def test_create_table_success(self, update_planner_setup):
        """Test successful table creation"""
        planner, metadata_manager, transaction, _, _, _ = update_planner_setup
        
        # Create test schema
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 100)
        schema.add_field("salary", FieldType.Integer, 0)
        
        # Create table
        create_data = CreateTable("employees", schema)
        result = planner.execute_create_table(create_data, transaction)
        
        assert result == 0
        
        # Verify table was created in metadata
        layout = metadata_manager.get_layout("employees", transaction)
        assert layout is not None
        assert len(layout.schema.fields) == 3
        assert "id" in layout.schema.fields
        assert "name" in layout.schema.fields
        assert "salary" in layout.schema.fields
    
    def test_create_table_duplicate_name(self, update_planner_setup):
        """Test creating table with duplicate name - should reveal error handling"""
        planner, metadata_manager, transaction, _, _, _ = update_planner_setup
        
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        
        # Create first table
        create_data1 = CreateTable("duplicate_table", schema)
        result1 = planner.execute_create_table(create_data1, transaction)
        assert result1 == 0
        
        # Try to create table with same name
        create_data2 = CreateTable("duplicate_table", schema)
        
        # This should either fail or overwrite - let's see what happens
        try:
            result2 = planner.execute_create_table(create_data2, transaction)
            print(f"Duplicate table creation returned: {result2}")
            # If it succeeds, it's a potential issue - should probably fail
        except Exception as e:
            print(f"Duplicate table creation failed as expected: {e}")
    
    def test_create_view_success(self, test_table_setup):
        """Test successful view creation"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Create some test data first
        insert_data = InsertData("students", ["id", "name", "age"], 
                               [Constant(1), Constant("Alice"), Constant(20)])
        planner.execute_insert(insert_data, transaction)
        
        # Create view query
        predicate = Predicate()
        age_term = Term(Expression("age"), Expression(Constant(18)))
        predicate.add_term(age_term)
        
        query_data = QueryData(["name", "age"], ["students"], predicate)
        
        # Create view
        create_view_data = CreateView("adult_students", query_data)
        result = planner.execute_create_view(create_view_data, transaction)
        
        assert result == 0
        
        # Verify view was created in metadata
        view_def = metadata_manager.get_view_definition("adult_students", transaction)
        assert view_def is not None
        print(f"Created view definition: {view_def}")
    
    def test_create_index_success(self, test_table_setup):
        """Test successful index creation"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Create index on id field
        create_index_data = CreateIndex("idx_students_id", "students", "id")
        result = planner.execute_create_index(create_index_data, transaction)
        
        assert result == 0
        
        # Verify index was created in metadata
        index_info = metadata_manager.get_index_info("students", transaction)
        assert "id" in index_info
        print(f"Created index info: {index_info}")
    
    def test_create_index_nonexistent_table(self, update_planner_setup):
        """Test creating index on nonexistent table"""
        planner, metadata_manager, transaction, _, _, _ = update_planner_setup
        
        create_index_data = CreateIndex("idx_fake_table", "nonexistent_table", "id")
        
        try:
            result = planner.execute_create_index(create_index_data, transaction)
            print(f"Index on nonexistent table returned: {result}")
            # If this succeeds, it's a bug - should fail
        except Exception as e:
            print(f"Index creation on nonexistent table failed as expected: {e}")
    
    def test_create_index_nonexistent_field(self, test_table_setup):
        """Test creating index on nonexistent field"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        create_index_data = CreateIndex("idx_bad_field", "students", "nonexistent_field")
        
        try:
            result = planner.execute_create_index(create_index_data, transaction)
            print(f"Index on nonexistent field returned: {result}")
            # If this succeeds, it's a bug - should fail
        except Exception as e:
            print(f"Index creation on nonexistent field failed as expected: {e}")


class TestBasicUpdatePlannerDML:
    """Test DML operations (INSERT, UPDATE, DELETE)"""
    
    def test_insert_success(self, test_table_setup):
        """Test successful record insertion"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert a record
        insert_data = InsertData("students", 
                               ["id", "name", "age", "gpa"], 
                               [Constant(1), Constant("Alice"), Constant(25), Constant("3.5")])
        
        result = planner.execute_insert(insert_data, transaction)
        assert result == 1  # Should return 1 for successful insert
        
        # Verify the record was inserted
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        found_record = False
        table_scan.before_first()
        while table_scan.next():
            if table_scan.get_int("id") == 1:
                assert table_scan.get_string("name") == "Alice"
                assert table_scan.get_int("age") == 25
                assert table_scan.get_string("gpa") == "3.5"
                found_record = True
                break
        
        table_scan.close()
        assert found_record, "Inserted record not found"
    
    def test_insert_multiple_records(self, test_table_setup):
        """Test inserting multiple records"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        students = [
            (1, "Alice", 25, "3.5"),
            (2, "Bob", 23, "3.2"),
            (3, "Charlie", 27, "3.8")
        ]
        
        # Insert multiple records
        for student_id, name, age, gpa in students:
            insert_data = InsertData("students", 
                                   ["id", "name", "age", "gpa"], 
                                   [Constant(student_id), Constant(name), Constant(age), Constant(gpa)])
            result = planner.execute_insert(insert_data, transaction)
            assert result == 1
        
        # Verify all records were inserted
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        found_ids = set()
        table_scan.before_first()
        while table_scan.next():
            found_ids.add(table_scan.get_int("id"))
        
        table_scan.close()
        assert found_ids == {1, 2, 3}
    
    def test_insert_wrong_field_count(self, test_table_setup):
        """Test insert with wrong number of fields - should reveal error handling"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Too few values
        insert_data = InsertData("students", 
                               ["id", "name"],  # Missing age and gpa
                               [Constant(1), Constant("Alice")])
        
        try:
            result = planner.execute_insert(insert_data, transaction)
            print(f"Insert with wrong field count returned: {result}")
            # This might succeed but cause issues later
        except Exception as e:
            print(f"Insert with wrong field count failed: {e}")
    
    def test_insert_nonexistent_table(self, update_planner_setup):
        """Test insert into nonexistent table"""
        planner, metadata_manager, transaction, _, _, _ = update_planner_setup
        
        insert_data = InsertData("nonexistent_table", 
                               ["id", "name"], 
                               [Constant(1), Constant("Alice")])
        
        try:
            result = planner.execute_insert(insert_data, transaction)
            print(f"Insert into nonexistent table returned: {result}")
        except Exception as e:
            print(f"Insert into nonexistent table failed as expected: {e}")
    
    def test_delete_with_predicate(self, test_table_setup):
        """Test deleting records with predicate"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        students = [
            (1, "Alice", 25, "3.5"),
            (2, "Bob", 23, "3.2"),
            (3, "Charlie", 27, "3.8"),
            (4, "Diana", 25, "3.6")
        ]
        
        for student_id, name, age, gpa in students:
            insert_data = InsertData("students", 
                                   ["id", "name", "age", "gpa"], 
                                   [Constant(student_id), Constant(name), Constant(age), Constant(gpa)])
            planner.execute_insert(insert_data, transaction)
        
        # Delete students with age = 25
        predicate = Predicate()
        age_term = Term(Expression("age"), Expression(Constant(25)))
        predicate.add_term(age_term)
        
        delete_data = DeleteData("students", predicate)
        result = planner.execute_delete(delete_data, transaction)
        
        assert result == 2  # Should delete Alice and Diana
        
        # Verify correct records were deleted
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        remaining_ids = set()
        table_scan.before_first()
        while table_scan.next():
            remaining_ids.add(table_scan.get_int("id"))
        
        table_scan.close()
        assert remaining_ids == {2, 3}  # Bob and Charlie should remain
    
    def test_delete_all_records(self, test_table_setup):
        """Test deleting all records with empty predicate"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        for i in range(5):
            insert_data = InsertData("students", 
                                   ["id", "name", "age", "gpa"], 
                                   [Constant(i), Constant(f"Student{i}"), Constant(20+i), Constant("3.0")])
            planner.execute_insert(insert_data, transaction)
        
        # Delete all records (empty predicate should match all)
        empty_predicate = Predicate()
        delete_data = DeleteData("students", empty_predicate)
        result = planner.execute_delete(delete_data, transaction)
        
        assert result == 5  # Should delete all 5 records
        
        # Verify table is empty
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        count = 0
        table_scan.before_first()
        while table_scan.next():
            count += 1
        
        table_scan.close()
        assert count == 0
    
    def test_delete_no_matches(self, test_table_setup):
        """Test delete with predicate that matches no records"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        insert_data = InsertData("students", 
                               ["id", "name", "age", "gpa"], 
                               [Constant(1), Constant("Alice"), Constant(25), Constant("3.5")])
        planner.execute_insert(insert_data, transaction)
        
        # Try to delete record with non-matching predicate
        predicate = Predicate()
        age_term = Term(Expression("age"), Expression(Constant(99)))  # No one is 99
        predicate.add_term(age_term)
        
        delete_data = DeleteData("students", predicate)
        result = planner.execute_delete(delete_data, transaction)
        
        assert result == 0  # Should delete 0 records
    
    def test_modify_with_predicate(self, test_table_setup):
        """Test modifying records with predicate"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        students = [
            (1, "Alice", 25, "3.5"),
            (2, "Bob", 25, "3.2"),
            (3, "Charlie", 27, "3.8")
        ]
        
        for student_id, name, age, gpa in students:
            insert_data = InsertData("students", 
                                   ["id", "name", "age", "gpa"], 
                                   [Constant(student_id), Constant(name), Constant(age), Constant(gpa)])
            planner.execute_insert(insert_data, transaction)
        
        # Update GPA for students with age = 25
        predicate = Predicate()
        age_term = Term(Expression("age"), Expression(Constant(25)))
        predicate.add_term(age_term)
        
        new_value = Expression(Constant("4.0"))
        modify_data = ModifyData("students", "gpa", new_value, predicate)
        result = planner.execute_modify(modify_data, transaction)
        
        assert result == 2  # Should update Alice and Bob
        
        # Verify the updates
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        updated_count = 0
        table_scan.before_first()
        while table_scan.next():
            if table_scan.get_int("age") == 25:
                assert table_scan.get_string("gpa") == "4.0"
                updated_count += 1
            elif table_scan.get_int("id") == 3:  # Charlie should be unchanged
                assert table_scan.get_string("gpa") == "3.8"
        
        table_scan.close()
        assert updated_count == 2
    
    def test_modify_integer_field(self, test_table_setup):
        """Test modifying integer field"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        insert_data = InsertData("students", 
                               ["id", "name", "age", "gpa"], 
                               [Constant(1), Constant("Alice"), Constant(25), Constant("3.5")])
        planner.execute_insert(insert_data, transaction)
        
        # Update age
        predicate = Predicate()
        id_term = Term(Expression("id"), Expression(Constant(1)))
        predicate.add_term(id_term)
        
        new_value = Expression(Constant(26))
        modify_data = ModifyData("students", "age", new_value, predicate)
        result = planner.execute_modify(modify_data, transaction)
        
        assert result == 1
        
        # Verify the update
        layout = metadata_manager.get_layout("students", transaction)
        table_scan = TableScan(transaction, "students", layout)
        
        table_scan.before_first()
        while table_scan.next():
            if table_scan.get_int("id") == 1:
                assert table_scan.get_int("age") == 26
                break
        
        table_scan.close()
    
    def test_modify_nonexistent_field(self, test_table_setup):
        """Test modify on nonexistent field - should reveal error handling"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        insert_data = InsertData("students", 
                               ["id", "name", "age", "gpa"], 
                               [Constant(1), Constant("Alice"), Constant(25), Constant("3.5")])
        planner.execute_insert(insert_data, transaction)
        
        predicate = Predicate()
        new_value = Expression(Constant("value"))
        modify_data = ModifyData("students", "nonexistent_field", new_value, predicate)
        
        try:
            result = planner.execute_modify(modify_data, transaction)
            print(f"Modify nonexistent field returned: {result}")
        except Exception as e:
            print(f"Modify nonexistent field failed as expected: {e}")


class TestBasicUpdatePlannerErrorHandling:
    """Test error handling and edge cases"""
    
    def test_operations_on_nonexistent_table(self, update_planner_setup):
        """Test all operations on nonexistent table"""
        planner, metadata_manager, transaction, _, _, _ = update_planner_setup
        
        # Try various operations on nonexistent table
        operations = []
        
        # Insert
        try:
            insert_data = InsertData("fake_table", ["id"], [Constant(1)])
            result = planner.execute_insert(insert_data, transaction)
            operations.append(f"Insert succeeded: {result}")
        except Exception as e:
            operations.append(f"Insert failed: {e}")
        
        # Delete
        try:
            delete_data = DeleteData("fake_table", Predicate())
            result = planner.execute_delete(delete_data, transaction)
            operations.append(f"Delete succeeded: {result}")
        except Exception as e:
            operations.append(f"Delete failed: {e}")
        
        # Modify
        try:
            modify_data = ModifyData("fake_table", "field", Expression(Constant("value")), Predicate())
            result = planner.execute_modify(modify_data, transaction)
            operations.append(f"Modify succeeded: {result}")
        except Exception as e:
            operations.append(f"Modify failed: {e}")
        
        print(f"Operations on nonexistent table: {operations}")
    
    def test_type_casting_issues(self, test_table_setup):
        """Test type casting in execute_modify - potential issue spotted"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # Insert test data
        insert_data = InsertData("students", 
                               ["id", "name", "age", "gpa"], 
                               [Constant(1), Constant("Alice"), Constant(25), Constant("3.5")])
        planner.execute_insert(insert_data, transaction)
        
        # The execute_modify method uses cast(UpdateScan, scan) without checking
        # This could cause issues if the scan is not actually an UpdateScan
        predicate = Predicate()
        new_value = Expression(Constant("4.0"))
        modify_data = ModifyData("students", "gpa", new_value, predicate)
        
        try:
            result = planner.execute_modify(modify_data, transaction)
            print(f"Type casting in modify worked: {result}")
        except Exception as e:
            print(f"Type casting in modify failed: {e}")
    
    def test_scan_type_verification(self, test_table_setup):
        """Test the scan type verification in different methods"""
        planner, metadata_manager, transaction, table_name, schema = test_table_setup
        
        # The execute_delete method checks isinstance(scan, UpdateScan)
        # The execute_insert method also checks isinstance(scan, UpdateScan)
        # But execute_modify uses cast without checking - inconsistent!
        
        # Test delete type checking
        try:
            delete_data = DeleteData("students", Predicate())
            result = planner.execute_delete(delete_data, transaction)
            print(f"Delete type checking passed: {result}")
        except ValueError as e:
            print(f"Delete type checking failed: {e}")
        
        # Test insert type checking
        try:
            insert_data = InsertData("students", ["id"], [Constant(1)])
            result = planner.execute_insert(insert_data, transaction)
            print(f"Insert type checking passed: {result}")
        except TypeError as e:
            print(f"Insert type checking failed: {e}")


class TestBasicUpdatePlannerTransactionSafety:
    """Test transaction safety and consistency"""
    
    def test_transaction_rollback_after_error(self, update_planner_setup):
        """Test that failed operations can be rolled back"""
        planner, metadata_manager, transaction, file_manager, log_manager, buffer_manager = update_planner_setup
        
        # Create a table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        
        create_table_data = CreateTable("test_rollback", schema)
        planner.execute_create_table(create_table_data, transaction)
        
        # Insert some data
        insert_data = InsertData("test_rollback", ["id", "name"], [Constant(1), Constant("Alice")])
        planner.execute_insert(insert_data, transaction)
        
        # Try an operation that might fail
        try:
            # This might fail due to constraint violation or other error
            bad_insert = InsertData("test_rollback", ["id", "name"], [Constant(1), Constant("Bob")])  # Duplicate ID
            planner.execute_insert(bad_insert, transaction)
        except Exception as e:
            print(f"Operation failed as expected: {e}")
            # Transaction should still be usable
            transaction.rollback()
            
            # Create new transaction and verify rollback worked
            new_transaction = Transaction(file_manager, log_manager, buffer_manager)
            
            # Check if first insert was rolled back
            layout = metadata_manager.get_layout("test_rollback", new_transaction)
            table_scan = TableScan(new_transaction, "test_rollback", layout)
            
            count = 0
            table_scan.before_first()
            while table_scan.next():
                count += 1
            
            table_scan.close()
            print(f"Records after rollback: {count}")
    
    def test_basic_transaction_usage(self, update_planner_setup):
        """Test basic transaction usage patterns"""
        planner, metadata_manager, transaction, file_manager, log_manager, buffer_manager = update_planner_setup
        
        # Create table and insert data in single transaction
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("value", FieldType.Varchar, 50)
        
        create_table_data = CreateTable("basic_tx_test", schema)
        planner.execute_create_table(create_table_data, transaction)
        
        # Insert multiple records
        for i in range(3):
            insert_data = InsertData("basic_tx_test", ["id", "value"], 
                                   [Constant(i), Constant(f"Value{i}")])
            result = planner.execute_insert(insert_data, transaction)
            assert result == 1
        
        # Commit and verify
        transaction.commit()
        
        # Create new transaction to verify persistence
        new_transaction = Transaction(file_manager, log_manager, buffer_manager)
        layout = metadata_manager.get_layout("basic_tx_test", new_transaction)
        table_scan = TableScan(new_transaction, "basic_tx_test", layout)
        
        count = 0
        table_scan.before_first()
        while table_scan.next():
            count += 1
        
        table_scan.close()
        assert count == 3
        print(f"Transaction committed {count} records successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])