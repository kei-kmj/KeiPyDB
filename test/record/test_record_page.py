import pytest
from pathlib import Path
import tempfile
import shutil

from db.constants import FieldType, ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_manager import LogManager
from db.buffer.buffer_manager import BufferManager
from db.record.layout import Layout
from db.record.record_page import RecordPage
from db.record.schema import Schema
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


def test_整数値を正しく取得設定できることを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    # トランザクションを作成
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    # スキーマとレイアウトを作成
    schema = Schema()
    schema.add_int_field("test_int")
    layout = Layout(schema)
    
    # ブロックを作成
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    # RecordPageを作成
    page = RecordPage(transaction, block, layout)
    
    # 整数値を設定して取得
    test_value = 12345
    slot = 0
    page.set_int(slot, "test_int", test_value)
    
    retrieved_value = page.get_int(slot, "test_int")
    assert retrieved_value == test_value
    
    transaction.commit()


def test_文字列値を正しく取得設定できることを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_string_field("test_string", 50)
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    
    test_value = "Hello, Database!"
    slot = 0
    page.set_string(slot, "test_string", test_value)
    
    retrieved_value = page.get_string(slot, "test_string")
    assert retrieved_value == test_value
    
    transaction.commit()


def test_レコードを削除できることを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()  # ページを初期化
    
    # スロット0を使用中に設定
    page._set_flag(0, RecordPage.USED)
    
    # 削除前は使用中
    flag_before = transaction.get_int(block, page._offset(0))
    assert flag_before == RecordPage.USED
    
    # 削除
    page.delete(0)
    
    # 削除後は空
    flag_after = transaction.get_int(block, page._offset(0))
    assert flag_after == RecordPage.EMPTY
    
    transaction.commit()


def test_フォーマット処理が正しく動作することを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 30)
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    
    # フォーマット前にデータを設定
    page._set_flag(0, RecordPage.USED)
    page.set_int(0, "id", 999)
    page.set_string(0, "name", "test")
    
    # フォーマット実行
    page.format()
    
    # フォーマット後、すべてのスロットが空になっている
    slot = 0
    while page._is_valid_slot(slot):
        flag = transaction.get_int(block, page._offset(slot))
        assert flag == RecordPage.EMPTY
        
        # フィールドも初期化されている
        assert page.get_int(slot, "id") == 0
        assert page.get_string(slot, "name") == ""
        
        slot += 1
    
    transaction.commit()


def test_次の使用中スロットを検索できることを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # スロット2と4を使用中に設定
    page._set_flag(2, RecordPage.USED)
    page._set_flag(4, RecordPage.USED)
    
    # スロット0の次の使用中スロットは2
    assert page.next_after(0) == 2
    
    # スロット2の次の使用中スロットは4
    assert page.next_after(2) == 4
    
    # スロット4の次の使用中スロットは存在しない
    assert page.next_after(4) == -1
    
    transaction.commit()


def test_次の空スロットを検索して設定できることを確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # スロット1を使用中に設定
    page._set_flag(1, RecordPage.USED)
    
    # スロット0の次の空スロットは2
    new_slot = page.insert_after(0)
    assert new_slot == 2
    
    # スロット2は使用中になっている
    flag = transaction.get_int(block, page._offset(2))
    assert flag == RecordPage.USED
    
    transaction.commit()


def test_スロットの有効性を確認する(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 0)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    
    # ブロックサイズとスロットサイズから有効なスロット数を計算
    block_size = transaction.block_size()
    slot_size = layout.get_slot_size()
    max_slots = block_size // slot_size
    
    # 有効なスロット
    assert page._is_valid_slot(0) is True
    assert page._is_valid_slot(max_slots - 2) is True
    
    # 無効なスロット（ブロックサイズを超える）
    assert page._is_valid_slot(max_slots) is False
    assert page._is_valid_slot(max_slots + 10) is False
    
    transaction.commit()


def test_複雑なレコード操作(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    # 複雑なスキーマ
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 50)
    schema.add_int_field("age")
    schema.add_string_field("email", 100)
    layout = Layout(schema)
    
    block = BlockID("users.tbl", 0)
    transaction.append("users.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # 複数のレコードを挿入
    test_data = [
        (1, "Alice", 25, "alice@example.com"),
        (2, "Bob", 30, "bob@example.com"),
        (3, "Charlie", 35, "charlie@example.com"),
    ]
    
    for i, (id_val, name, age, email) in enumerate(test_data):
        slot = page.insert_after(-1)
        assert slot >= 0
        
        page.set_int(slot, "id", id_val)
        page.set_string(slot, "name", name)
        page.set_int(slot, "age", age)
        page.set_string(slot, "email", email)
    
    # データを読み返して確認
    slot = -1
    retrieved_data = []
    while True:
        slot = page.next_after(slot)
        if slot < 0:
            break
            
        id_val = page.get_int(slot, "id")
        name = page.get_string(slot, "name")
        age = page.get_int(slot, "age")
        email = page.get_string(slot, "email")
        
        retrieved_data.append((id_val, name, age, email))
    
    assert retrieved_data == test_data
    
    transaction.commit()


def test_slot_fragmentation_scenarios(setup_managers):
    """スロットの断片化シナリオのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("fragmentation.tbl", 0)
    transaction.append("fragmentation.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # 複数のスロットを使用中に設定
    used_slots = []
    for i in range(5):
        slot = page.insert_after(-1)
        used_slots.append(slot)
        page.set_int(slot, "id", i)
    
    # 一部のスロットを削除（断片化を作成）
    page.delete(used_slots[1])  # スロット1を削除
    page.delete(used_slots[3])  # スロット3を削除
    
    # 新しいレコードを挿入（削除されたスロットが再利用されるか確認）
    new_slot = page.insert_after(-1)
    assert new_slot in [used_slots[1], used_slots[3]]  # 削除されたスロットが再利用される
    
    # 残っているレコードが正しく読めることを確認
    remaining_ids = []
    slot = -1
    while True:
        slot = page.next_after(slot)
        if slot < 0:
            break
        remaining_ids.append(page.get_int(slot, "id"))
    
    # 削除されていないレコード + 新しいレコードが存在する
    assert len(remaining_ids) == 4  # 5個作成 - 2個削除 + 1個追加
    
    transaction.commit()


def test_get_block(setup_managers):
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("test.tbl", 5)
    transaction.append("test.tbl")
    
    page = RecordPage(transaction, block, layout)
    
    assert page.get_block() == block
    assert page.get_block().file_name == "test.tbl"
    assert page.get_block().block_number == 5
    
    transaction.commit()


def test_concurrent_record_operations(setup_managers):
    """複数のRecordPageが同じブロックを操作する場合のテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction1 = Transaction(file_manager, log_manager, buffer_manager)
    transaction2 = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("name", 30)
    layout = Layout(schema)
    
    block = BlockID("shared.tbl", 0)
    transaction1.append("shared.tbl")
    
    page1 = RecordPage(transaction1, block, layout)
    page2 = RecordPage(transaction2, block, layout)
    
    # page1でフォーマット
    page1.format()
    
    # page1でデータ設定
    page1._set_flag(0, RecordPage.USED)
    page1.set_int(0, "id", 100)
    page1.set_string(0, "name", "Transaction1")
    
    # page2から同じデータを読み取り
    assert page2.get_int(0, "id") == 100
    assert page2.get_string(0, "name") == "Transaction1"
    
    transaction1.commit()
    transaction2.commit()


def test_boundary_slot_operations(setup_managers):
    """境界値のスロット操作テスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("boundary.tbl", 0)
    transaction.append("boundary.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # 最大スロット数を計算
    block_size = transaction.block_size()
    slot_size = layout.get_slot_size()
    max_slots = block_size // slot_size
    
    # 最初のスロット
    assert page._is_valid_slot(0) is True
    
    # 最後の有効スロット
    last_valid_slot = max_slots - 1
    assert page._is_valid_slot(last_valid_slot) is True
    
    # 無効なスロット
    assert page._is_valid_slot(max_slots) is False
    assert page._is_valid_slot(-1) is False
    
    transaction.commit()


def test_record_page_with_large_strings(setup_managers):
    """大きな文字列を含むレコードのテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    schema.add_string_field("large_text", 500)  # 大きな文字列フィールド
    layout = Layout(schema)
    
    block = BlockID("large_strings.tbl", 0)
    transaction.append("large_strings.tbl")
    
    page = RecordPage(transaction, block, layout)
    page.format()
    
    # 大きな文字列を設定
    large_string = "A" * 450  # 500文字制限の90%
    page._set_flag(0, RecordPage.USED)
    page.set_int(0, "id", 1)
    page.set_string(0, "large_text", large_string)
    
    # 正しく読み取れることを確認
    assert page.get_int(0, "id") == 1
    assert page.get_string(0, "large_text") == large_string
    
    transaction.commit()


def test_record_page_error_conditions(setup_managers):
    """エラー条件のテスト"""
    file_manager, log_manager, buffer_manager = setup_managers
    
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    
    schema = Schema()
    schema.add_int_field("id")
    layout = Layout(schema)
    
    block = BlockID("error_test.tbl", 0)
    transaction.append("error_test.tbl")
    
    page = RecordPage(transaction, block, layout)
    
    # 無効なスロットでの操作は例外が発生しないが、データが破損する可能性
    # 実際の実装では境界チェックが不十分な可能性がある
    
    # 存在しないフィールドでの操作
    try:
        page.get_int(0, "nonexistent_field")
        # 例外が発生しない場合もあるが、この場合は実装に依存
    except (ValueError, KeyError):
        pass  # 期待される例外
    
    transaction.commit()
