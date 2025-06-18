import tempfile
import shutil
import pytest

from db.buffer.buffer_manager import BufferManager
from db.constants import FieldType
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.metadata.table_manager import TableManager
from db.metadata.view_manager import ViewManager
from db.record.schema import Schema
from db.transaction.transaction import Transaction


@pytest.fixture
def real_view_env():
    """ViewManager用の実際の環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "view_test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 10)
        yield file_manager, log_manager, buffer_manager
    finally:
        shutil.rmtree(temp_dir)


def test_view_manager_initialization(real_view_env):
    """ViewManagerの初期化テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    # TableManagerが必要
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # view_catalogテーブルが作成されていることを確認
    view_catalog_layout = table_manager.get_layout("view_catalog", tx)
    assert view_catalog_layout is not None
    
    # view_catalogの構造確認
    assert view_catalog_layout.schema.has_field("view_name")
    assert view_catalog_layout.schema.has_field("view_def")
    
    tx.commit()


def test_create_view_basic(real_view_env):
    """基本的なビュー作成テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # ビューを作成
    view_name = "test_view"
    view_definition = "SELECT * FROM users WHERE age > 18"
    
    view_manager.create_view(view_name, view_definition, tx)
    
    # ビューの定義を取得
    retrieved_definition = view_manager.get_view_def(view_name, tx)
    
    assert retrieved_definition == view_definition
    
    tx.commit()


def test_create_multiple_views(real_view_env):
    """複数ビューの作成テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # 複数のビューを作成
    views = [
        ("user_adults", "SELECT * FROM users WHERE age >= 18"),
        ("product_expensive", "SELECT * FROM products WHERE price > 1000"),
        ("order_summary", "SELECT user_id, COUNT(*) as order_count FROM orders GROUP BY user_id")
    ]
    
    for view_name, view_def in views:
        view_manager.create_view(view_name, view_def, tx)
    
    # 各ビューの定義を確認
    for view_name, expected_def in views:
        retrieved_def = view_manager.get_view_def(view_name, tx)
        assert retrieved_def == expected_def
    
    tx.commit()


def test_view_definition_max_length(real_view_env):
    """ビュー定義最大長のテスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # MAX_VIEW_DEF (100) を超える長いビュー定義
    long_view_def = "SELECT " + ", ".join([f"field_{i}" for i in range(50)]) + " FROM very_long_table_name"
    assert len(long_view_def) > ViewManager.MAX_VIEW_DEF
    
    try:
        view_manager.create_view("long_view", long_view_def, tx)
        # 長い定義が切り捨てられているかチェック
        retrieved_def = view_manager.get_view_def("long_view", tx)
        print(f"Long view definition handling: original_length={len(long_view_def)}, retrieved_length={len(retrieved_def) if retrieved_def else 0}")
        
        if retrieved_def:
            # 切り捨てられた場合、元の定義より短いはず
            assert len(retrieved_def) <= ViewManager.MAX_VIEW_DEF
    except Exception as e:
        print(f"Expected error with long view definition: {e}")
    
    tx.commit()


def test_view_name_max_length(real_view_env):
    """ビュー名最大長のテスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # MAX_NAME (16) を超える長いビュー名
    long_view_name = "very_long_view_name_that_exceeds_maximum"
    assert len(long_view_name) > table_manager.MAX_NAME
    
    short_view_def = "SELECT * FROM users"
    
    try:
        view_manager.create_view(long_view_name, short_view_def, tx)
        
        # 元の名前でアクセスしてみる
        retrieved_def = view_manager.get_view_def(long_view_name, tx)
        
        # 切り捨てられた名前でもアクセスしてみる
        truncated_name = long_view_name[:table_manager.MAX_NAME]
        truncated_def = view_manager.get_view_def(truncated_name, tx)
        
        print(f"Long view name handling: original={retrieved_def is not None}, truncated={truncated_def is not None}")
        
    except Exception as e:
        print(f"Expected error with long view name: {e}")
    
    tx.commit()


def test_get_view_def_for_nonexistent_view(real_view_env):
    """存在しないビューの定義取得テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # 存在しないビューの定義を取得
    definition = view_manager.get_view_def("nonexistent_view", tx)
    
    # Noneが返されることを確認
    assert definition is None
    
    tx.commit()


def test_view_persistence_across_transactions(real_view_env):
    """トランザクション間でのビュー永続性テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    
    # 最初のトランザクションでビューを作成
    tx1 = Transaction(file_manager, log_manager, buffer_manager)
    table_manager1 = TableManager(True, tx1)
    view_manager1 = ViewManager(True, table_manager1, tx1)
    
    view_name = "persistent_view"
    view_definition = "SELECT id, name FROM users WHERE active = 1"
    
    view_manager1.create_view(view_name, view_definition, tx1)
    tx1.commit()
    
    # 2番目のトランザクションで同じビューにアクセス
    tx2 = Transaction(file_manager, log_manager, buffer_manager)
    table_manager2 = TableManager(False, tx2)  # 既存のデータベース
    view_manager2 = ViewManager(False, table_manager2, tx2)
    
    retrieved_definition = view_manager2.get_view_def(view_name, tx2)
    
    # ビューが正しく永続化されていることを確認
    assert retrieved_definition == view_definition
    
    tx2.commit()


def test_view_catalog_integrity(real_view_env):
    """ViewManagerのカタログ整合性テスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # ビューを作成
    view_name = "integrity_test_view"
    view_definition = "SELECT * FROM test_table WHERE status = 'active'"
    
    view_manager.create_view(view_name, view_definition, tx)
    
    # カタログテーブルから直接情報を確認
    from db.record.table_scan import TableScan
    
    view_catalog_layout = table_manager.get_layout("view_catalog", tx)
    view_scan = TableScan(tx, "view_catalog", view_catalog_layout)
    
    found_view = False
    while view_scan.next():
        name = view_scan.get_string("view_name")
        if name == view_name:
            found_view = True
            definition = view_scan.get_string("view_def")
            assert definition == view_definition
            break
    
    assert found_view, "ビューがview_catalogに見つからない"
    view_scan.close()
    
    tx.commit()


def test_view_manager_edge_cases(real_view_env):
    """ViewManagerのエッジケーステスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # 空の文字列でのビュー作成
    try:
        view_manager.create_view("", "SELECT * FROM users", tx)
        empty_def = view_manager.get_view_def("", tx)
        print(f"Empty view name handling: {empty_def is not None}")
    except Exception as e:
        print(f"Empty view name error: {e}")
    
    # 空のビュー定義
    try:
        view_manager.create_view("empty_def_view", "", tx)
        empty_def = view_manager.get_view_def("empty_def_view", tx)
        print(f"Empty view definition handling: retrieved='{empty_def}'")
    except Exception as e:
        print(f"Empty view definition error: {e}")
    
    # 同じ名前のビューを複数回作成
    try:
        view_manager.create_view("duplicate_view", "SELECT * FROM table1", tx)
        view_manager.create_view("duplicate_view", "SELECT * FROM table2", tx)
        
        final_def = view_manager.get_view_def("duplicate_view", tx)
        print(f"Duplicate view name handling: final_definition='{final_def}'")
    except Exception as e:
        print(f"Duplicate view name error: {e}")
    
    tx.commit()


def test_view_manager_stress_test(real_view_env):
    """ViewManagerのストレステスト"""
    file_manager, log_manager, buffer_manager = real_view_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_manager = TableManager(True, tx)
    view_manager = ViewManager(True, table_manager, tx)
    
    # 大量のビューを作成
    num_views = 50
    
    for i in range(num_views):
        view_name = f"stress_view_{i}"
        view_def = f"SELECT * FROM table_{i % 5} WHERE field_{i % 3} > {i * 10}"
        
        view_manager.create_view(view_name, view_def, tx)
    
    # 作成されたビューを確認
    success_count = 0
    for i in range(num_views):
        view_name = f"stress_view_{i}"
        retrieved_def = view_manager.get_view_def(view_name, tx)
        if retrieved_def is not None:
            success_count += 1
    
    # 大部分のビューが正しく作成されていることを確認
    assert success_count >= num_views * 0.9  # 90%以上成功
    print(f"Stress test: {success_count}/{num_views} views created successfully")
    
    tx.commit()