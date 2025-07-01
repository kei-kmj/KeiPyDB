"""
Simple server tests to isolate core production issues
"""
import tempfile
import shutil
from db.server.keipy_db import KeiPyDB

def test_basic_server_functionality():
    """Test basic server functionality to identify core issues"""
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Testing in directory: {temp_dir}")
        
        # Test 1: Basic initialization
        print("=== Test 1: Basic Initialization ===")
        db = KeiPyDB(temp_dir)
        print("✓ KeiPyDB initialization successful")
        
        # Test 2: Transaction creation
        print("=== Test 2: Transaction Creation ===")
        tx = db.new_transaction()
        print("✓ Transaction creation successful")
        
        # Test 3: Basic SQL operations
        print("=== Test 3: Basic SQL Operations ===")
        planner = db.get_planner()
        
        # Create table
        try:
            result = planner.execute_update("CREATE TABLE simple_test (id varchar(10))", tx)
            print(f"✓ CREATE TABLE result: {result}")
        except Exception as e:
            print(f"✗ CREATE TABLE error: {e}")
            return
        
        # Insert data
        try:
            result = planner.execute_update("INSERT INTO simple_test (id) VALUES ('test1')", tx)
            print(f"✓ INSERT result: {result}")
        except Exception as e:
            print(f"✗ INSERT error: {e}")
        
        # Commit transaction
        try:
            tx.commit()
            print("✓ Transaction commit successful")
        except Exception as e:
            print(f"✗ Transaction commit error: {e}")
        
        # Test 4: Query data
        print("=== Test 4: Query Data ===")
        tx2 = db.new_transaction()
        try:
            plan = planner.create_query_plan("SELECT id FROM simple_test", tx2)
            scan = plan.open()
            
            results = []
            scan.before_first()
            while scan.next():
                id_val = scan.get_string('id')
                results.append(id_val)
                print(f"Found: {id_val}")
            
            scan.close()
            tx2.commit()
            print(f"✓ Query successful, found {len(results)} records")
            
            # Check for string handling issues
            if results and results[0] != "test1":
                print(f"⚠ WARNING: String handling issue - Expected 'test1', got '{results[0]}'")
                
        except Exception as e:
            print(f"✗ Query error: {e}")
        
    finally:
        shutil.rmtree(temp_dir)

def test_database_recovery():
    """Test database recovery functionality"""
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"=== Test: Database Recovery ===")
        
        # Create initial database
        print("Creating initial database...")
        db1 = KeiPyDB(temp_dir)
        tx1 = db1.new_transaction()
        planner1 = db1.get_planner()
        
        # Add some data
        planner1.execute_update("CREATE TABLE recovery_test (data varchar(20))", tx1)
        planner1.execute_update("INSERT INTO recovery_test (data) VALUES ('persistent')", tx1)
        tx1.commit()
        print("✓ Initial data created")
        
        # Delete first instance
        del db1
        print("✓ First database instance deleted")
        
        # Recreate database (should recover)
        print("Recovering database...")
        try:
            db2 = KeiPyDB(temp_dir)
            print("✓ Database recovery successful")
            
            # Verify data persistence
            tx2 = db2.new_transaction()
            planner2 = db2.get_planner()
            plan = planner2.create_query_plan("SELECT data FROM recovery_test", tx2)
            scan = plan.open()
            
            found_data = []
            scan.before_first()
            while scan.next():
                data = scan.get_string('data')
                found_data.append(data)
            
            scan.close()
            tx2.commit()
            
            print(f"✓ Recovery verification: found {len(found_data)} records")
            if found_data:
                print(f"Data: {found_data[0]}")
            
        except Exception as e:
            print(f"✗ Database recovery error: {e}")
            
    finally:
        shutil.rmtree(temp_dir)

def test_start_server_issues():
    """Test StartServer specific issues"""
    from db.server.start_server import StartServer
    import sys
    from unittest.mock import patch
    
    print("=== Test: StartServer Issues ===")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Test with proper directory
        with patch.object(sys, 'argv', ['start_server.py', temp_dir]):
            import io
            captured_output = io.StringIO()
            
            with patch('sys.stdout', captured_output):
                try:
                    StartServer.main()
                    output = captured_output.getvalue()
                    print("✓ StartServer.main() completed")
                    
                    # Look for specific issues in output
                    if "id = 'hello'" in output:
                        print("⚠ WARNING: String quoting issue detected in output")
                    
                    if "scan.close()" in output:  # This suggests there's an error
                        print("⚠ WARNING: Potential scan close issue in code")
                        
                except Exception as e:
                    print(f"✗ StartServer error: {e}")
                    output = captured_output.getvalue()
                    if output:
                        print(f"Partial output: {output[:200]}...")
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_basic_server_functionality()
    print()
    test_database_recovery()
    print()
    test_start_server_issues()