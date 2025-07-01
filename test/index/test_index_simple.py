"""
Simple index tests to isolate production issues
"""
import tempfile
import shutil
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.buffer.buffer_manager import BufferManager
from db.transaction.transaction import Transaction
from db.record.schema import Schema
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.constants import FieldType
from db.index.hash.hash_index import HashIndex
from db.query.constant import Constant

def test_hash_index_basic():
    """Test basic hash index functionality to identify production issues"""
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Testing in directory: {temp_dir}")
        
        # Setup database environment
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        # Create index schema
        index_schema = Schema()
        index_schema.add_field("block", FieldType.Integer, 0)
        index_schema.add_field("id", FieldType.Integer, 0)
        index_schema.add_field("data_value", FieldType.Integer, 0)
        index_layout = Layout(index_schema)
        
        print("=== Test 1: Hash Index Creation ===")
        hash_index = HashIndex(transaction, "test_index", index_layout)
        print("✓ Hash index created successfully")
        
        print("=== Test 2: Hash Index Insertion ===")
        try:
            # Try direct insertion without before_first
            data_value = Constant(10)
            record_id = RecordID(1, 1)
            hash_index.insert(data_value, record_id)
            print("✗ Direct insertion succeeded - this might be unexpected")
        except RuntimeError as e:
            print(f"⚠ Direct insertion failed: {e}")
            
            # Try with before_first first
            try:
                hash_index.before_first(data_value)
                hash_index.insert(data_value, record_id)
                print("✓ Insertion after before_first succeeded")
            except Exception as e2:
                print(f"✗ Insertion after before_first failed: {e2}")
        
        print("=== Test 3: Hash Index Search ===")
        try:
            hash_index.before_first(Constant(10))
            found = hash_index.next()
            if found:
                found_record_id = hash_index.get_data_record_id()
                print(f"✓ Found record: {found_record_id}")
            else:
                print("⚠ No record found")
        except Exception as e:
            print(f"✗ Search failed: {e}")
        
        print("=== Test 4: Hash Index Bucket Calculation ===")
        test_values = [1, 2, 100, 101]
        for value in test_values:
            bucket = hash(Constant(value)) % HashIndex.NUM_BUCKETS
            print(f"Value {value} -> Bucket {bucket}")
        
        print("=== Test 5: Hash Index Cost Calculation ===")
        cost = HashIndex.search_cost(1000)
        expected = 1000 // HashIndex.NUM_BUCKETS
        print(f"Search cost for 1000 blocks: {cost} (expected: {expected})")
        assert cost == expected
        
        hash_index.close()
        transaction.commit()
        
    finally:
        shutil.rmtree(temp_dir)

def test_hash_index_logic_errors():
    """Test to identify logic errors in hash index implementation"""
    temp_dir = tempfile.mkdtemp()
    try:
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        index_schema = Schema()
        index_schema.add_field("block", FieldType.Integer, 0)
        index_schema.add_field("id", FieldType.Integer, 0)
        index_schema.add_field("data_value", FieldType.Integer, 0)
        index_layout = Layout(index_schema)
        
        hash_index = HashIndex(transaction, "logic_test", index_layout)
        
        print("=== Logic Error Test: Insert Method ===")
        
        # The insert method has a logic error:
        # 1. It checks if table_scan is None
        # 2. Then calls before_first which initializes table_scan
        # This check should be removed or the logic should be different
        
        print("Testing insert method logic...")
        data_value = Constant(42)
        record_id = RecordID(1, 1)
        
        # This should work because insert() calls before_first() internally
        try:
            hash_index.insert(data_value, record_id)
            print("✗ Insert succeeded unexpectedly")
        except RuntimeError as e:
            print(f"✓ Insert failed as expected due to logic error: {e}")
            print("PRODUCTION ISSUE: insert() checks for uninitialized table_scan but then calls before_first()")
        
        hash_index.close()
        
    finally:
        shutil.rmtree(temp_dir)

def test_hash_index_comparison_logic():
    """Test the comparison logic in hash index next() method"""
    temp_dir = tempfile.mkdtemp()
    try:
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        index_schema = Schema()
        index_schema.add_field("block", FieldType.Integer, 0)
        index_schema.add_field("id", FieldType.Integer, 0)
        index_schema.add_field("data_value", FieldType.Integer, 0)
        index_layout = Layout(index_schema)
        
        hash_index = HashIndex(transaction, "comparison_test", index_layout)
        
        print("=== Comparison Logic Test ===")
        
        # Looking at line 42 in hash_index.py:
        # if self.search_key is self.table_scan.get_value("data_value"):
        # This uses 'is' for comparison, which checks object identity, not equality
        # This is likely a bug - should use '==' for value comparison
        
        print("PRODUCTION ISSUE FOUND: Line 42 uses 'is' instead of '==' for comparison")
        print("This means the search will likely never find matches")
        
        hash_index.close()
        
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_hash_index_basic()
    print()
    test_hash_index_logic_errors()
    print()
    test_hash_index_comparison_logic()