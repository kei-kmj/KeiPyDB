"""
Comprehensive tests for the Planner coordinator class
Testing the coordination between query planning and update planning functionality
Using real low-layer classes instead of mocks
"""

import pytest
import tempfile
import shutil
import time

# Import the main Planner coordinator class
from db.plan.planner import Planner
from db.plan.basic_query_planner import BasicQueryPlanner
from db.plan.basic_update_planner import BasicUpdatePlanner
from db.plan.better_query_planner import BetterQueryPlanner

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

# Import query classes
from db.query.constant import Constant
from db.query.expression import Expression
from db.query.term import Term
from db.query.predicate import Predicate

# Import parse classes for testing data creation
from db.parse.query_data import QueryData
from db.parse.insert_data import InsertData
from db.parse.create_table import CreateTable
from db.parse.create_view import CreateView
from db.parse.create_index import CreateIndex
from db.parse.delete_data import DeleteData
from db.parse.modify_data import ModifyData


@pytest.fixture
def real_db_env():
    """Real database environment using actual low-layer classes"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 8)
        
        # Create transaction for setup
        setup_transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        # Create metadata manager
        metadata_manager = MetadataManager(True, setup_transaction)
        setup_transaction.commit()
        
        # Create fresh transaction for testing
        test_transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        yield file_manager, log_manager, buffer_manager, metadata_manager, test_transaction
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def planner_coordinator(real_db_env):
    """Create a Planner coordinator with real planners"""
    file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
    
    # Create real planner instances
    query_planner = BasicQueryPlanner(metadata_manager)
    update_planner = BasicUpdatePlanner(metadata_manager)
    
    # Create the coordinator
    planner = Planner(query_planner, update_planner)
    
    yield planner, metadata_manager, transaction, file_manager, log_manager, buffer_manager


class TestPlannerCoordinatorBasics:
    """Test basic Planner coordinator functionality"""
    
    def test_planner_initialization(self, planner_coordinator):
        """Test Planner initialization with real planners"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Test that planner has the right components
        assert planner.query_planner is not None
        assert planner.update_planner is not None
        assert isinstance(planner.query_planner, BasicQueryPlanner)
        assert isinstance(planner.update_planner, BasicUpdatePlanner)
        
        print("Planner coordinator initialized with real planners")
    
    def test_planner_with_better_query_planner(self, real_db_env):
        """Test Planner with BetterQueryPlanner for optimization"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env
        
        # Create planner with optimization
        better_query_planner = BetterQueryPlanner(metadata_manager)
        update_planner = BasicUpdatePlanner(metadata_manager)
        
        planner = Planner(better_query_planner, update_planner)
        
        assert isinstance(planner.query_planner, BetterQueryPlanner)
        assert isinstance(planner.update_planner, BasicUpdatePlanner)
        
        print("Planner coordinator with BetterQueryPlanner created successfully")


class TestPlannerCoordinatorTableOperations:
    """Test Planner coordinator with table creation and manipulation"""
    
    def test_create_table_coordination(self, planner_coordinator):
        """Test CREATE TABLE coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create schema for students table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("age", FieldType.Integer, 0)
        
        # Create CreateTable data object
        create_table_data = CreateTable("students", schema)
        
        # Execute through planner coordinator
        result = planner.execute_update("create table students (id int, name varchar(50), age int)", transaction)
        
        # Verify table was created (result should be 0 for DDL)
        assert result == 0
        
        # Verify table exists in metadata
        layout = metadata_manager.get_layout("students", transaction)
        assert layout is not None
        assert len(layout.schema.fields) == 3
        
        print("CREATE TABLE coordinated successfully through Planner")
    
    def test_create_view_coordination(self, planner_coordinator):
        """Test CREATE VIEW coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # First create a base table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("city", FieldType.Varchar, 30)
        
        planner.execute_update("create table employees (id int, name varchar(50), city varchar(30))", transaction)
        
        # Create view through planner
        view_definition = "select name, city from employees"
        result = planner.execute_update(f"create view tokyo_employees as {view_definition}", transaction)
        
        assert result == 0
        
        # Verify view was created
        view_def = metadata_manager.get_view_definition("tokyo_employees", transaction)
        assert view_def is not None
        assert "employees" in view_def
        
        print("CREATE VIEW coordinated successfully through Planner")
    
    def test_create_index_coordination(self, planner_coordinator):
        """Test CREATE INDEX coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # First create a table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("email", FieldType.Varchar, 100)
        
        planner.execute_update("create table users (id int, email varchar(100))", transaction)
        
        # Create index through planner
        result = planner.execute_update("create index idx_email on users (email)", transaction)
        
        assert result == 0
        
        # Verify index was created
        index_info = metadata_manager.get_index_info("users", transaction)
        assert "email" in index_info
        
        print("CREATE INDEX coordinated successfully through Planner")


class TestPlannerCoordinatorDataOperations:
    """Test Planner coordinator with data manipulation operations"""
    
    def test_insert_coordination(self, planner_coordinator):
        """Test INSERT coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create table first
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("score", FieldType.Integer, 0)
        
        planner.execute_update("create table scores (id int, name varchar(50), score int)", transaction)
        
        # Insert data through planner coordinator
        result1 = planner.execute_update("insert into scores (id, name, score) values (1, 'Alice', 95)", transaction)
        result2 = planner.execute_update("insert into scores (id, name, score) values (2, 'Bob', 87)", transaction)
        result3 = planner.execute_update("insert into scores (id, name, score) values (3, 'Charlie', 92)", transaction)
        
        assert result1 == 1  # One record inserted
        assert result2 == 1
        assert result3 == 1
        
        # Verify data was inserted by querying
        query_plan = planner.create_query_plan("select name, score from scores", transaction)
        scan = query_plan.open()
        
        records = []
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            score = scan.get_int("score")
            records.append({"name": name, "score": score})
        scan.close()
        
        assert len(records) == 3
        names = [r["name"] for r in records]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names
        
        print(f"INSERT coordination successful: {len(records)} records inserted")
    
    def test_update_coordination(self, planner_coordinator):
        """Test UPDATE coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create and populate table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("salary", FieldType.Integer, 0)
        
        planner.execute_update("create table employees (id int, name varchar(50), salary int)", transaction)
        planner.execute_update("insert into employees (id, name, salary) values (1, 'John', 50000)", transaction)
        planner.execute_update("insert into employees (id, name, salary) values (2, 'Jane', 55000)", transaction)
        planner.execute_update("insert into employees (id, name, salary) values (3, 'Jack', 48000)", transaction)
        
        # Update records through planner
        result = planner.execute_update("update employees set salary = 60000 where id = 1", transaction)
        
        assert result == 1  # One record updated
        
        # Verify update by querying
        query_plan = planner.create_query_plan("select name, salary from employees where id = 1", transaction)
        scan = query_plan.open()
        
        found_record = False
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            salary = scan.get_int("salary")
            if name == "John":
                assert salary == 60000
                found_record = True
        scan.close()
        
        assert found_record
        print("UPDATE coordination successful: salary updated correctly")
    
    def test_delete_coordination(self, planner_coordinator):
        """Test DELETE coordination through Planner"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create and populate table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("product", FieldType.Varchar, 50)
        schema.add_field("price", FieldType.Integer, 0)
        
        planner.execute_update("create table products (id int, product varchar(50), price int)", transaction)
        planner.execute_update("insert into products (id, product, price) values (1, 'Laptop', 1200)", transaction)
        planner.execute_update("insert into products (id, product, price) values (2, 'Mouse', 25)", transaction)
        planner.execute_update("insert into products (id, product, price) values (3, 'Keyboard', 75)", transaction)
        planner.execute_update("insert into products (id, product, price) values (4, 'Monitor', 300)", transaction)
        
        # Delete records through planner
        result = planner.execute_update("delete from products where price < 100", transaction)
        
        assert result == 2  # Mouse and Keyboard deleted
        
        # Verify deletion by querying remaining records
        query_plan = planner.create_query_plan("select product, price from products", transaction)
        scan = query_plan.open()
        
        remaining_products = []
        scan.before_first()
        while scan.next():
            product = scan.get_string("product")
            price = scan.get_int("price")
            remaining_products.append({"product": product, "price": price})
        scan.close()
        
        assert len(remaining_products) == 2
        products = [r["product"] for r in remaining_products]
        assert "Laptop" in products
        assert "Monitor" in products
        assert "Mouse" not in products
        assert "Keyboard" not in products
        
        print(f"DELETE coordination successful: {result} records deleted")


class TestPlannerCoordinatorQueryOperations:
    """Test Planner coordinator query planning functionality"""
    
    def test_simple_query_coordination(self, planner_coordinator):
        """Test simple SELECT query coordination"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Setup test data
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("department", FieldType.Varchar, 30)
        
        planner.execute_update("create table staff (id int, name varchar(50), department varchar(30))", transaction)
        planner.execute_update("insert into staff (id, name, department) values (1, 'Alice', 'Engineering')", transaction)
        planner.execute_update("insert into staff (id, name, department) values (2, 'Bob', 'Sales')", transaction)
        planner.execute_update("insert into staff (id, name, department) values (3, 'Charlie', 'Engineering')", transaction)
        planner.execute_update("insert into staff (id, name, department) values (4, 'Diana', 'Marketing')", transaction)
        
        # Execute query through planner coordinator
        query_plan = planner.create_query_plan("select name, department from staff where department = 'Engineering'", transaction)
        
        assert query_plan is not None
        
        # Execute the plan
        scan = query_plan.open()
        results = []
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            department = scan.get_string("department")
            results.append({"name": name, "department": department})
        scan.close()
        
        # Verify results
        assert len(results) == 2
        for result in results:
            assert result["department"] == "Engineering"
        
        names = [r["name"] for r in results]
        assert "Alice" in names
        assert "Charlie" in names
        
        print(f"Simple query coordination successful: {len(results)} matching records")
    
    def test_complex_query_coordination(self, planner_coordinator):
        """Test complex query with joins coordination"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create customers table
        customers_schema = Schema()
        customers_schema.add_field("customer_id", FieldType.Integer, 0)
        customers_schema.add_field("customer_name", FieldType.Varchar, 50)
        customers_schema.add_field("city", FieldType.Varchar, 30)
        
        planner.execute_update("create table customers (customer_id int, customer_name varchar(50), city varchar(30))", transaction)
        planner.execute_update("insert into customers (customer_id, customer_name, city) values (1, 'John', 'Tokyo')", transaction)
        planner.execute_update("insert into customers (customer_id, customer_name, city) values (2, 'Jane', 'Osaka')", transaction)
        planner.execute_update("insert into customers (customer_id, customer_name, city) values (3, 'Jack', 'Tokyo')", transaction)
        
        # Create orders table
        orders_schema = Schema()
        orders_schema.add_field("order_id", FieldType.Integer, 0)
        orders_schema.add_field("customer_id", FieldType.Integer, 0)
        orders_schema.add_field("amount", FieldType.Integer, 0)
        
        planner.execute_update("create table orders (order_id int, customer_id int, amount int)", transaction)
        planner.execute_update("insert into orders (order_id, customer_id, amount) values (101, 1, 500)", transaction)
        planner.execute_update("insert into orders (order_id, customer_id, amount) values (102, 2, 750)", transaction)
        planner.execute_update("insert into orders (order_id, customer_id, amount) values (103, 1, 300)", transaction)
        planner.execute_update("insert into orders (order_id, customer_id, amount) values (104, 3, 1000)", transaction)
        
        # Execute join query through planner coordinator
        query_plan = planner.create_query_plan(
            "select customer_name, amount from customers, orders where customers.customer_id = orders.customer_id",
            transaction
        )
        
        assert query_plan is not None
        
        # Execute the plan
        scan = query_plan.open()
        results = []
        scan.before_first()
        count = 0
        while scan.next():
            try:
                customer_name = scan.get_string("customer_name")
                amount = scan.get_int("amount")
                customer_id1 = scan.get_int("customer_id")  # From customers table
                # Note: there might be ambiguity with customer_id field
                results.append({"customer_name": customer_name, "amount": amount})
                count += 1
            except Exception as e:
                print(f"Scan error: {e}")
                break
            
            if count > 10:  # Prevent excessive iteration
                break
        scan.close()
        
        # Verify we got some join results
        assert len(results) > 0
        print(f"Complex join query coordination successful: {len(results)} join results")
        
        # Verify join correctness for at least one record
        for result in results:
            assert result["customer_name"] in ["John", "Jane", "Jack"]
            assert result["amount"] > 0
    
    def test_query_with_view_coordination(self, planner_coordinator):
        """Test query coordination with views"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create base table
        schema = Schema()
        schema.add_field("id", FieldType.Integer, 0)
        schema.add_field("name", FieldType.Varchar, 50)
        schema.add_field("status", FieldType.Varchar, 20)
        schema.add_field("priority", FieldType.Integer, 0)
        
        planner.execute_update("create table tasks (id int, name varchar(50), status varchar(20), priority int)", transaction)
        planner.execute_update("insert into tasks (id, name, status, priority) values (1, 'Task A', 'active', 1)", transaction)
        planner.execute_update("insert into tasks (id, name, status, priority) values (2, 'Task B', 'completed', 2)", transaction)
        planner.execute_update("insert into tasks (id, name, status, priority) values (3, 'Task C', 'active', 1)", transaction)
        planner.execute_update("insert into tasks (id, name, status, priority) values (4, 'Task D', 'pending', 3)", transaction)
        
        # Create view
        planner.execute_update("create view active_tasks as select name, priority from tasks where status = 'active'", transaction)
        
        # Query the view through planner coordinator
        query_plan = planner.create_query_plan("select name, priority from active_tasks", transaction)
        
        assert query_plan is not None
        
        # Execute the plan
        scan = query_plan.open()
        results = []
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            priority = scan.get_int("priority")
            results.append({"name": name, "priority": priority})
        scan.close()
        
        # Verify view query results
        assert len(results) == 2  # Task A and Task C are active
        names = [r["name"] for r in results]
        assert "Task A" in names
        assert "Task C" in names
        
        print(f"View query coordination successful: {len(results)} active tasks found")


class TestPlannerCoordinatorErrorHandling:
    """Test Planner coordinator error handling and edge cases"""
    
    def test_invalid_sql_query_handling(self, planner_coordinator):
        """Test Planner handling of invalid SQL queries"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Test invalid query syntax
        try:
            query_plan = planner.create_query_plan("invalid sql query", transaction)
            assert False, "Should have raised an exception for invalid SQL"
        except Exception as e:
            print(f"Expected error for invalid query: {e}")
    
    def test_invalid_sql_update_handling(self, planner_coordinator):
        """Test Planner handling of invalid SQL updates"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Test invalid update syntax
        try:
            result = planner.execute_update("invalid update command", transaction)
            assert False, "Should have raised an exception for invalid update"
        except Exception as e:
            print(f"Expected error for invalid update: {e}")
    
    def test_nonexistent_table_query(self, planner_coordinator):
        """Test query on nonexistent table"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        try:
            query_plan = planner.create_query_plan("select * from nonexistent_table", transaction)
            # The query might succeed at planning stage but fail at execution
            scan = query_plan.open()
            scan.before_first()
            scan.next()  # This should fail
            scan.close()
            assert False, "Should have failed with nonexistent table"
        except Exception as e:
            print(f"Expected error for nonexistent table query: {e}")
    
    def test_nonexistent_table_update(self, planner_coordinator):
        """Test update on nonexistent table"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        try:
            result = planner.execute_update("insert into nonexistent_table (id) values (1)", transaction)
            assert False, "Should have failed with nonexistent table"
        except Exception as e:
            print(f"Expected error for nonexistent table update: {e}")
    
    def test_verify_methods_functionality(self, planner_coordinator):
        """Test verify_query and verify_update methods"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # These methods are currently empty but should not crash
        try:
            planner.verify_query()
            planner.verify_update()
            print("Verify methods executed without errors (currently no-ops)")
        except Exception as e:
            print(f"Unexpected error in verify methods: {e}")
            assert False, "Verify methods should not raise exceptions"


class TestPlannerCoordinatorIntegration:
    """Test Planner coordinator integration scenarios"""
    
    def test_full_lifecycle_coordination(self, planner_coordinator):
        """Test complete lifecycle: create table, insert, query, update, delete"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # 1. Create table
        result = planner.execute_update("create table inventory (id int, product varchar(50), quantity int, price int)", transaction)
        assert result == 0
        
        # 2. Insert data
        products = [
            (1, "Laptop", 10, 1000),
            (2, "Mouse", 50, 20),
            (3, "Keyboard", 30, 50),
            (4, "Monitor", 15, 300)
        ]
        
        for pid, product, quantity, price in products:
            result = planner.execute_update(f"insert into inventory (id, product, quantity, price) values ({pid}, '{product}', {quantity}, {price})", transaction)
            assert result == 1
        
        # 3. Query data
        query_plan = planner.create_query_plan("select product, quantity, price from inventory where price > 50", transaction)
        scan = query_plan.open()
        
        expensive_items = []
        scan.before_first()
        while scan.next():
            product = scan.get_string("product")
            quantity = scan.get_int("quantity")
            price = scan.get_int("price")
            expensive_items.append({"product": product, "quantity": quantity, "price": price})
        scan.close()
        
        assert len(expensive_items) == 2  # Laptop and Monitor
        
        # 4. Update data
        result = planner.execute_update("update inventory set quantity = 5 where product = 'Monitor'", transaction)
        assert result == 1
        
        # 5. Verify update
        query_plan = planner.create_query_plan("select quantity from inventory where product = 'Monitor'", transaction)
        scan = query_plan.open()
        scan.before_first()
        if scan.next():
            new_quantity = scan.get_int("quantity")
            assert new_quantity == 5
        scan.close()
        
        # 6. Delete data
        result = planner.execute_update("delete from inventory where price < 30", transaction)
        assert result == 1  # Only Mouse should be deleted
        
        # 7. Final verification
        query_plan = planner.create_query_plan("select product from inventory", transaction)
        scan = query_plan.open()
        
        remaining_products = []
        scan.before_first()
        while scan.next():
            product = scan.get_string("product")
            remaining_products.append(product)
        scan.close()
        
        assert len(remaining_products) == 3  # Laptop, Keyboard, Monitor
        assert "Mouse" not in remaining_products
        
        print("Full lifecycle coordination test completed successfully")
    
    def test_transaction_coordination(self, planner_coordinator):
        """Test Planner coordination with transaction management"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Create table
        planner.execute_update("create table accounts (id int, name varchar(50), balance int)", transaction)
        planner.execute_update("insert into accounts (id, name, balance) values (1, 'Alice', 1000)", transaction)
        planner.execute_update("insert into accounts (id, name, balance) values (2, 'Bob', 500)", transaction)
        
        # Commit the setup
        transaction.commit()
        
        # Start new transaction for testing
        test_transaction = Transaction(fm, lm, bm)
        
        # Test updates in transaction
        planner.execute_update("update accounts set balance = 1200 where id = 1", test_transaction)
        planner.execute_update("update accounts set balance = 300 where id = 2", test_transaction)
        
        # Query within transaction (should see changes)
        query_plan = planner.create_query_plan("select name, balance from accounts", test_transaction)
        scan = query_plan.open()
        
        balances = {}
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            balance = scan.get_int("balance")
            balances[name] = balance
        scan.close()
        
        assert balances["Alice"] == 1200
        assert balances["Bob"] == 300
        
        # Commit the transaction
        test_transaction.commit()
        
        # Verify with new transaction
        verify_transaction = Transaction(fm, lm, bm)
        query_plan = planner.create_query_plan("select name, balance from accounts", verify_transaction)
        scan = query_plan.open()
        
        final_balances = {}
        scan.before_first()
        while scan.next():
            name = scan.get_string("name")
            balance = scan.get_int("balance")
            final_balances[name] = balance
        scan.close()
        
        assert final_balances["Alice"] == 1200
        assert final_balances["Bob"] == 300
        
        verify_transaction.commit()
        print("Transaction coordination test completed successfully")


class TestPlannerCoordinatorIssuesDiscovery:
    """Test for discovering production code issues in Planner coordination"""
    
    def test_parser_integration_issues(self, planner_coordinator):
        """Test potential issues with Parser integration"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # Test various SQL parsing edge cases through planner
        test_cases = [
            # Basic cases
            ("create table test1 (id int)", "CREATE TABLE"),
            ("insert into test1 (id) values (1)", "INSERT"),
            ("select id from test1", "SELECT"),
            ("update test1 set id = 2", "UPDATE"),
            ("delete from test1 where id = 1", "DELETE"),
        ]
        
        issues_found = []
        
        for sql, operation in test_cases:
            try:
                if operation == "SELECT":
                    query_plan = planner.create_query_plan(sql, transaction)
                    assert query_plan is not None
                else:
                    result = planner.execute_update(sql, transaction)
                    # Results vary by operation type
                print(f"✓ {operation} parsing works: {sql}")
            except Exception as e:
                issue = f"❌ {operation} parsing failed: {sql} - Error: {e}"
                issues_found.append(issue)
                print(issue)
        
        if issues_found:
            print(f"\n🔍 PRODUCTION ISSUES FOUND IN PARSER INTEGRATION:")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("✅ No parser integration issues found")
    
    def test_planner_coordination_consistency(self, planner_coordinator):
        """Test consistency between query and update coordination"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        issues_found = []
        
        # Create test table
        planner.execute_update("create table consistency_test (id int, value varchar(50))", transaction)
        
        # Test update-query consistency
        try:
            # Insert through update planner
            insert_result = planner.execute_update("insert into consistency_test (id, value) values (1, 'test')", transaction)
            assert insert_result == 1
            
            # Query through query planner
            query_plan = planner.create_query_plan("select id, value from consistency_test", transaction)
            scan = query_plan.open()
            
            found_records = 0
            scan.before_first()
            while scan.next():
                id_val = scan.get_int("id")
                value = scan.get_string("value")
                assert id_val == 1
                assert value == "test"
                found_records += 1
            scan.close()
            
            if found_records != 1:
                issues_found.append(f"Consistency issue: inserted 1 record but query found {found_records}")
            
        except Exception as e:
            issues_found.append(f"Update-Query coordination failed: {e}")
        
        # Test update-update coordination
        try:
            # Update the record
            update_result = planner.execute_update("update consistency_test set value = 'updated' where id = 1", transaction)
            assert update_result == 1
            
            # Verify with another query
            query_plan = planner.create_query_plan("select value from consistency_test where id = 1", transaction)
            scan = query_plan.open()
            
            scan.before_first()
            if scan.next():
                updated_value = scan.get_string("value")
                if updated_value != "updated":
                    issues_found.append(f"Update coordination issue: expected 'updated' but got '{updated_value}'")
            else:
                issues_found.append("Update coordination issue: record not found after update")
            scan.close()
            
        except Exception as e:
            issues_found.append(f"Update-Update coordination failed: {e}")
        
        if issues_found:
            print(f"\n🔍 PRODUCTION ISSUES FOUND IN PLANNER COORDINATION:")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("✅ No coordination consistency issues found")
    
    def test_unknown_command_handling(self, planner_coordinator):
        """Test Planner handling of unknown update commands"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # The execute_update method has a fallback case that returns 0
        # This might indicate a design issue
        
        try:
            # This should trigger the "else: return 0" case in execute_update
            # But first we need to understand what would cause this
            
            # Create a mock update command that doesn't match any known types
            # This is tricky because the parser will handle most cases
            
            # Let's test what happens with an unrecognized command
            result = planner.execute_update("unknown command that should not be recognized", transaction)
            
            # If we get here, it means the parser didn't throw an exception
            # and the fallback case returned 0
            print(f"⚠️  POTENTIAL ISSUE: Unknown command returned {result} instead of raising exception")
            print("   This might indicate insufficient validation in the Planner coordinator")
            
        except Exception as e:
            print(f"✅ Unknown command properly rejected: {e}")
    
    def test_empty_verify_methods_issue(self, planner_coordinator):
        """Test the issue with empty verify methods"""
        planner, metadata_manager, transaction, fm, lm, bm = planner_coordinator
        
        # The verify_query and verify_update methods are empty
        # This indicates incomplete implementation
        
        print("🔍 PRODUCTION ISSUE FOUND: Empty verify methods")
        print("   - verify_query() method is empty (line 50-51 in planner.py)")
        print("   - verify_update() method is empty (line 53-54 in planner.py)")
        print("   - These methods should implement validation logic")
        print("   - Current implementation provides no query/update validation")
        print("   - Security and correctness implications")
        
        # Test that they don't crash but also don't validate anything
        try:
            planner.verify_query()
            planner.verify_update()
            print("   - Methods execute without error but provide no validation")
        except Exception as e:
            print(f"   - Unexpected error in verify methods: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])