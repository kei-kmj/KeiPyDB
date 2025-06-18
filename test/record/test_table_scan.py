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


def test_テーブルスキャンの初期化ができる(setup_managers):
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


def test_存在しないテーブルでエラーが発生する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    # 存在しないテーブルファイルを明示的に作成しない
    # TableScanの初期化でFileNotFoundErrorが発生するはず
    with pytest.raises(FileNotFoundError) as exc_info:
        # まず空のファイルを作成してから削除
        transaction.append("nonexistent.tbl")
        transaction.commit()
        
        # 新しいトランザクションで存在しないテーブルにアクセス
        new_transaction = Transaction(file_manager, log_manager, buffer_manager)
        # ファイルを削除
        import os
        os.remove(os.path.join(file_manager.db_directory, "nonexistent.tbl"))
        
        table_scan = TableScan(new_transaction, "nonexistent", layout)
    
    assert "Table nonexistent does not exist" in str(exc_info.value)


def test_レコードの挿入と読み取り(setup_managers):
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


def test_get_valueとset_value(setup_managers):
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


def test_レコードの削除(setup_managers):
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


def test_move_to_ridとget_rid(setup_managers):
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


def test_複数ブロックにまたがる操作(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    # 小さいブロックサイズで再初期化
    block_size = 512  # 小さいブロックサイズ
    file_manager = FileManager(file_manager.db_directory, block_size)
    log_manager = LogManager(file_manager, "test.log")
    buffer_manager = BufferManager(file_manager, log_manager, 10)
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("data", 100)  # 大きめのフィールド
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "large_table", layout)
    
    # 多数のレコードを挿入（複数ブロックに分散）
    num_records = 50
    for i in range(num_records):
        table_scan.insert()
        table_scan.set_int("id", i)
        table_scan.set_string("data", f"Record {i} with some data")
    
    # すべてのレコードを読み取り
    table_scan.before_first()
    count = 0
    while table_scan.next():
        assert table_scan.get_int("id") == count
        assert table_scan.get_string("data") == f"Record {count} with some data"
        count += 1
    
    assert count == num_records
    
    table_scan.close()
    transaction.commit()


def test_不正なフィールドタイプでのエラー(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    # 不正なフィールドタイプを設定
    schema.add_field("weird_field", 999, 10)
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "test_table", layout)
    table_scan.insert()
    
    # get_valueで不正なフィールドタイプを処理しようとするとエラー
    with pytest.raises(ValueError) as exc_info:
        table_scan.get_value("weird_field")
    assert "Unknown field type 999" in str(exc_info.value)
    
    table_scan.close()
    transaction.commit()


def test_初期化されていないrecord_pageでのエラー(setup_managers):
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


def test_table_scan_with_transaction_rollback(setup_managers):
    """トランザクションロールバック時の動作テスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "rollback_test", layout)
    
    # データを挿入
    table_scan.insert()
    table_scan.set_int("id", 1)
    table_scan.set_string("name", "Test Data")
    
    # ロールバック
    table_scan.close()
    transaction.rollback()
    
    # 新しいトランザクションでデータを確認
    new_transaction = Transaction(file_manager, log_manager, buffer_manager)
    new_table_scan = TableScan(new_transaction, "rollback_test", layout)
    
    # ロールバックされたデータは存在しない
    new_table_scan.before_first()
    assert not new_table_scan.next()
    
    new_table_scan.close()
    new_transaction.commit()


def test_table_scan_set_value_with_unknown_field(setup_managers):
    """未知フィールドでのset_valueのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("known_field")
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "unknown_field_test", layout)
    table_scan.insert()
    
    # スキーマにないフィールドでset_valueを呼び出し
    # 現在の実装では値の型から推定して設定する
    table_scan.set_value("unknown_int", Constant(42))
    table_scan.set_value("unknown_string", Constant("test"))
    
    # 実際に設定されるかは実装に依存
    # ここではエラーが発生しないことを確認
    
    table_scan.close()
    transaction.commit()


def test_table_scan_insert_when_no_space(setup_managers):
    """スペース不足時の挿入テスト"""
    # 小さいブロックサイズでテスト
    file_manager, log_manager, buffer_manager = setup_managers
    small_file_manager = FileManager(file_manager.db_directory, 256)  # 小さいブロック
    small_log_manager = LogManager(small_file_manager, "small.log")
    small_buffer_manager = BufferManager(small_file_manager, small_log_manager, 5)
    
    transaction = Transaction(small_file_manager, small_log_manager, small_buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("large_data", 200)  # 大きなフィールド
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "large_records", layout)
    
    # ブロックの容量を超えるまでレコードを挿入
    records_inserted = 0
    try:
        for i in range(100):  # 十分な数を試行
            table_scan.insert()
            table_scan.set_int("id", i)
            table_scan.set_string("large_data", "X" * 150)
            records_inserted += 1
    except Exception as e:
        # エラーが発生した場合、いくつかのレコードは挿入されているはず
        pass
    
    # 少なくとも1つのレコードは挿入されている
    assert records_inserted >= 1
    
    table_scan.close()
    transaction.commit()


def test_table_scan_concurrent_access(setup_managers):
    """並行アクセスのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    # 最初のトランザクションでデータを作成
    transaction1 = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("data", 30)
    layout = Layout(schema)
    
    table_scan1 = TableScan(transaction1, "concurrent_test", layout)
    
    # データを挿入
    table_scan1.insert()
    table_scan1.set_int("id", 1)
    table_scan1.set_string("data", "Initial Data")
    
    table_scan1.close()
    transaction1.commit()
    
    # 第2のトランザクションで読み取り
    transaction2 = Transaction(file_manager, log_manager, buffer_manager)
    table_scan2 = TableScan(transaction2, "concurrent_test", layout)
    
    table_scan2.before_first()
    assert table_scan2.next()
    assert table_scan2.get_int("id") == 1
    assert table_scan2.get_string("data") == "Initial Data"
    
    # 第3のトランザクションで同時にアクセス
    transaction3 = Transaction(file_manager, log_manager, buffer_manager)
    table_scan3 = TableScan(transaction3, "concurrent_test", layout)
    
    # 新しいデータを追加
    table_scan3.insert()
    table_scan3.set_int("id", 2)
    table_scan3.set_string("data", "Second Data")
    
    table_scan2.close()
    table_scan3.close()
    transaction2.commit()
    transaction3.commit()


def test_table_scan_stress_operations(setup_managers):
    """ストレステスト（大量操作）"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("description", 100)
    layout = Layout(schema)
    
    table_scan = TableScan(transaction, "stress_test", layout)
    
    # 大量のレコードを挿入
    num_records = 1000
    for i in range(num_records):
        table_scan.insert()
        table_scan.set_int("id", i)
        table_scan.set_string("description", f"Record number {i} with some description")
    
    # 全レコードを読み取り
    table_scan.before_first()
    count = 0
    while table_scan.next():
        assert table_scan.get_int("id") == count
        expected_desc = f"Record number {count} with some description"
        assert table_scan.get_string("description") == expected_desc
        count += 1
    
    assert count == num_records
    
    table_scan.close()
    transaction.commit()
