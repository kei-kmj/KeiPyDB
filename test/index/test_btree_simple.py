"""
Simple B-tree index tests to identify production issues
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
from db.index.btree.btree_index import BtreeIndex
from db.query.constant import Constant

def test_btree_index_basic():
    """Test basic B-tree index functionality"""
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Testing B-tree in directory: {temp_dir}")
        
        # Setup database environment
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        print("=== Test 1: B-tree Index Creation ===")
        try:
            # Create leaf schema
            leaf_schema = Schema()
            leaf_schema.add_field("data_value", FieldType.Integer, 0)
            leaf_schema.add_field("block", FieldType.Integer, 0)
            leaf_schema.add_field("id", FieldType.Integer, 0)
            leaf_layout = Layout(leaf_schema)
            
            btree_index = BtreeIndex(transaction, "test_btree", leaf_layout)
            print("✓ B-tree index created successfully")
            
            # Check if files were created
            leaf_table = "test_btreeleaf"
            dir_table = "test_btreedir"
            
            leaf_size = transaction.size(leaf_table)
            dir_size = transaction.size(dir_table)
            
            print(f"✓ Leaf table size: {leaf_size}")
            print(f"✓ Directory table size: {dir_size}")
            
        except Exception as e:
            print(f"✗ B-tree creation failed: {e}")
            return
        
        print("=== Test 2: B-tree Index Insertion ===")
        try:
            data_value = Constant(10)
            record_id = RecordID(1, 1)
            
            btree_index.insert(data_value, record_id)
            print("✓ B-tree insertion succeeded")
            
        except Exception as e:
            print(f"✗ B-tree insertion failed: {e}")
        
        print("=== Test 3: B-tree Index Search ===")
        try:
            btree_index.before_first(Constant(10))
            found = btree_index.next()
            
            if found:
                found_record_id = btree_index.get_data_record_id()
                print(f"✓ B-tree search found record: {found_record_id}")
            else:
                print("⚠ B-tree search found no records")
                
        except Exception as e:
            print(f"✗ B-tree search failed: {e}")
        
        print("=== Test 4: B-tree Multiple Insertions ===")
        try:
            test_values = [5, 15, 3, 7, 12, 18]
            for i, value in enumerate(test_values):
                btree_index.insert(Constant(value), RecordID(1, i + 2))
            
            print(f"✓ Inserted {len(test_values)} additional values")
            
            # Try to find each value
            found_count = 0
            for value in test_values:
                btree_index.before_first(Constant(value))
                if btree_index.next():
                    found_count += 1
            
            print(f"✓ Found {found_count} out of {len(test_values)} values")
            
        except Exception as e:
            print(f"✗ Multiple insertions test failed: {e}")
        
        btree_index.close()
        transaction.commit()
        
    finally:
        shutil.rmtree(temp_dir)

def test_btree_schema_issues():
    """Test B-tree schema initialization issues"""
    temp_dir = tempfile.mkdtemp()
    try:
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        print("=== B-tree Schema Issues Test ===")
        
        # Looking at btree_index.py lines 33-34:
        # dir_schema.add("block", self.leaf_layout.get_schema())
        # dir_schema.add("data_value", self.leaf_layout.get_schema())
        
        # This looks wrong - it's adding the entire schema as a field type
        # Should probably be adding specific field types
        
        leaf_schema = Schema()
        leaf_schema.add_field("data_value", FieldType.Integer, 0)
        leaf_schema.add_field("block", FieldType.Integer, 0)
        leaf_schema.add_field("id", FieldType.Integer, 0)
        leaf_layout = Layout(leaf_schema)
        
        try:
            btree_index = BtreeIndex(transaction, "schema_test", leaf_layout)
            print("⚠ B-tree creation succeeded despite potential schema issues")
            btree_index.close()
        except Exception as e:
            print(f"✗ B-tree creation failed due to schema issues: {e}")
            print("PRODUCTION ISSUE: dir_schema.add() calls seem incorrect")
        
    finally:
        shutil.rmtree(temp_dir)

def test_btree_overflow_logic():
    """Test B-tree overflow and node logic"""
    temp_dir = tempfile.mkdtemp()
    try:
        file_manager = FileManager(temp_dir, 1024)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        transaction = Transaction(file_manager, log_manager, buffer_manager)
        
        print("=== B-tree Overflow Logic Test ===")
        
        # Looking at btree_index.py line 30:
        # node.format(block, Node.Overflow)
        # This seems wrong - formatting a new leaf node as overflow?
        
        print("PRODUCTION ISSUE: New leaf nodes are formatted as Overflow nodes")
        print("This seems incorrect - new nodes should probably be Valid nodes")
        
        # Also line 47:
        # root.insert_directory(Slot.First, min_value, self.ROOT_BLOCK_INDEX)
        # Using ROOT_BLOCK_INDEX (0) as block number, but it should probably be
        # the actual leaf block number
        
        print("PRODUCTION ISSUE: Root directory entry uses ROOT_BLOCK_INDEX instead of leaf block")
        
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_btree_index_basic()
    print()
    test_btree_schema_issues()
    print()
    test_btree_overflow_logic()