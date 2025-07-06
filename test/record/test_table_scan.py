import pytest
import tempfile
import shutil

from db.constants import FieldType
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.buffer.buffer_manager import BufferManager
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


@pytest.fixture
def setup_db_dir():
    """テスト用の一時ディレクトリを作成"""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def setup_managers(setup_db_dir):
    """FileManager, LogManager, BufferManagerを作成"""
    block_size = 4096
    num_buffers = 10
    
    file_manager = FileManager(setup_db_dir, block_size)
    log_manager = LogManager(file_manager, "test.log")
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers)
    
    return file_manager, log_manager, buffer_manager


def test_table_scan_can_be_initialized(setup_managers):
    """TableScanの初期化テスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    layout = Layout(schema)
    
    # テーブルスキャンを作成（新しいテーブル）
    table_scan = TableScan(transaction, "users", layout)
    
    assert table_scan.file_name == "users.tbl"
    assert table_scan.layout == layout
    assert table_scan.current_slot == -1
    assert table_scan.record_page is not None
    
    table_scan.close()
    transaction.commit()


def test_record_insertion_and_reading(setup_managers):
    """レコードの挿入と読み取りテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    schema.add_int_field("age")
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "users", layout)
    
    # レコードを挿入
    table_scan.insert()
    table_scan.set_int("id", 1)
    table_scan.set_string("name", "Alice")
    table_scan.set_int("age", 25)
    
    table_scan.insert()
    table_scan.set_int("id", 2)
    table_scan.set_string("name", "Bob")
    table_scan.set_int("age", 30)
    
    # 最初から読み取り
    table_scan.before_first()
    
    # 1番目のレコード
    assert table_scan.next() is True
    assert table_scan.get_int("id") == 1
    assert table_scan.get_string("name") == "Alice"
    assert table_scan.get_int("age") == 25
    
    # 2番目のレコード
    assert table_scan.next() is True
    assert table_scan.get_int("id") == 2
    assert table_scan.get_string("name") == "Bob"
    assert table_scan.get_int("age") == 30
    
    # もうレコードはない
    assert table_scan.next() is False
    
    table_scan.close()
    transaction.commit()


def test_get_value_and_set_value(setup_managers):
    """get_valueとset_valueのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("int_field")
    schema.add_string_field("string_field", 50)
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    
    # Constantを使った値の設定
    table_scan.insert()
    table_scan.set_value("int_field", Constant(42))
    table_scan.set_value("string_field", Constant("Hello"))
    
    # 値の取得
    int_value = table_scan.get_value("int_field")
    string_value = table_scan.get_value("string_field")
    
    assert int_value.as_int() == 42
    assert string_value.as_string() == "Hello"
    
    table_scan.close()
    transaction.commit()


def test_has_field(setup_managers):
    """has_fieldのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    
    assert table_scan.has_field("id") is True
    assert table_scan.has_field("name") is True
    assert table_scan.has_field("nonexistent") is False
    
    table_scan.close()
    transaction.commit()


def test_record_deletion(setup_managers):
    """レコード削除のテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    
    # 3つのレコードを挿入
    for i in range(1, 4):
        table_scan.insert()
        table_scan.set_int("id", i)
    
    # 2番目のレコードを削除
    table_scan.before_first()
    table_scan.next()  # id=1
    table_scan.next()  # id=2
    table_scan.delete()
    
    # 残りのレコードを確認
    table_scan.before_first()
    remaining_ids = []
    while table_scan.next():
        remaining_ids.append(table_scan.get_int("id"))
    
    assert remaining_ids == [1, 3]
    
    table_scan.close()
    transaction.commit()


def test_move_to_rid_and_get_rid(setup_managers):
    """RIDによる移動と取得のテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    
    # レコードを挿入してRIDを記憶
    table_scan.insert()
    table_scan.set_int("id", 100)
    rid1 = table_scan.get_rid()
    
    table_scan.insert()
    table_scan.set_int("id", 200)
    rid2 = table_scan.get_rid()
    
    # 別の場所に移動
    table_scan.before_first()
    
    # RIDを使って特定のレコードに移動
    table_scan.move_to_rid(rid2)
    assert table_scan.get_int("id") == 200
    
    table_scan.move_to_rid(rid1)
    assert table_scan.get_int("id") == 100
    
    table_scan.close()
    transaction.commit()


def test_runtime_error_with_uninitialized_record_page(setup_managers):
    """RecordPageが初期化されていない場合のRuntimeErrorテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    
    # record_pageを明示的にNoneに設定（通常は起こらない）
    table_scan.record_page = None
    
    # 各メソッドでRuntimeErrorが発生することを確認
    with pytest.raises(RuntimeError) as exc_info:
        table_scan.next()
    assert "Record page is not initialized" in str(exc_info.value)
    
    with pytest.raises(RuntimeError) as exc_info:
        table_scan.get_int("id")
    assert "Record page is not initialized" in str(exc_info.value)
    
    with pytest.raises(RuntimeError) as exc_info:
        table_scan.set_int("id", 1)
    assert "Record page is not initialized" in str(exc_info.value)
    
    transaction.commit()

