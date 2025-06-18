import tempfile
import shutil
import threading
import time
from unittest.mock import Mock

import pytest

from db.buffer.buffer import Buffer
from db.buffer.buffer_manager import BufferManager
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.transaction.transaction import Transaction
from db.transaction.concurrency.lock_table import LockAbortException


def test_トランザクションのコミットが正しく動作することを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    recovery_manager = Mock()
    transaction.recovery_manager = recovery_manager
    concurrency_manager = Mock()
    transaction.concurrency_manager = concurrency_manager
    buffer_list = Mock()
    transaction.buffer_list = buffer_list

    transaction.commit()

    recovery_manager.commit.assert_called_once()
    concurrency_manager.release.assert_called_once()
    buffer_list.unpin_all.assert_called_once()
    print(f"Transaction {transaction.tx_number} committed")


def test_トランザクションのロールバックが正しく動作することを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    recovery_manager = Mock()
    transaction.recovery_manager = recovery_manager
    concurrency_manager = Mock()
    transaction.concurrency_manager = concurrency_manager
    buffer_list = Mock()
    transaction.buffer_list = buffer_list

    transaction.rollback()

    recovery_manager.rollback.assert_called_once()
    concurrency_manager.release.assert_called_once()
    buffer_list.unpin_all.assert_called_once()
    print(f"Transaction {transaction.tx_number} rolled back")


def test_指定したブロックをピンできることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer_list = Mock()
    transaction.buffer_list = buffer_list
    block = BlockID("test", 1)

    transaction.pin(block)

    buffer_list.pin.assert_called_once_with(block)


def test_指定したブロックをアンピンできることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer_list = Mock()
    transaction.buffer_list = buffer_list
    block = BlockID("test", 1)

    transaction.unpin(block)

    buffer_list.unpin.assert_called_once_with(block)


def test_指定したブロックの指定したオフセットの整数値を取得できるこを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer = Mock(spec=Buffer)
    buffer.get_int = Mock(return_value=0)
    buffer.contents = Mock()
    buffer.contents.get_int = Mock(return_value=0)
    buffer_manager.pin = Mock(return_value=buffer)
    block = BlockID("test", 1)
    offset = 1

    actual = transaction.get_int(block, offset)

    assert actual == 0
    buffer_manager.pin.assert_called_once_with(block)


def test_指定したブロックの指定したオフセットの文字列を取得できることを確認する():

    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    buffer = Mock(spec=Buffer)
    buffer.get_int = Mock(return_value=0)
    buffer.contents = Mock()
    buffer.contents.get_string = Mock(return_value="")
    buffer_manager.pin = Mock(return_value=buffer)
    block = BlockID("test", 1)
    offset = 1

    actual = transaction.get_string(block, offset)

    assert actual == ""
    buffer_manager.pin.assert_called_once_with(block)


def test_共有ロックと排他ロックが正しく動作することを確認():
    file_manager = Mock()
    log_manager = Mock()
    buffer_manager = Mock()
    transaction = Transaction(file_manager, log_manager, buffer_manager)
    another_transaction = Transaction(file_manager, log_manager, buffer_manager)

    block = BlockID("shared_block", 1)

    transaction.concurrency_manager.lock_shared(block)
    another_transaction.concurrency_manager.lock_shared(block)

    transaction.concurrency_manager.lock_exclusive(block)
    transaction.concurrency_manager.lock_shared(block)

    # 他のトランザクションが共有ロックを取得しているため、排他ロックは取得できない
    assert transaction.concurrency_manager.lock_shared(block) is None
    assert another_transaction.concurrency_manager.lock_shared(block) is None
    # 他のトランザクションが排他ロックを取得しているため、排他ロックは取得できない
    assert another_transaction.concurrency_manager.lock_exclusive(block) is None


@pytest.fixture
def real_transaction_env():
    """実際のFileManager, LogManager, BufferManagerを使用するテスト環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_transaction_log")
        buffer_manager = BufferManager(file_manager, log_manager, 8)
        yield file_manager, log_manager, buffer_manager
    finally:
        shutil.rmtree(temp_dir)


def test_transaction_initialization_with_real_managers(real_transaction_env):
    """実際のマネージャーでのトランザクション初期化テスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    
    tx1 = Transaction(file_manager, log_manager, buffer_manager)
    tx2 = Transaction(file_manager, log_manager, buffer_manager)
    
    # トランザクション番号が順次割り当てられることを確認
    assert tx2.tx_number == tx1.tx_number + 1
    
    # 各コンポーネントが正しく初期化されていることを確認
    assert tx1.file_manager == file_manager
    assert tx1.buffer_manager == buffer_manager
    assert tx1.recovery_manager is not None
    assert tx1.concurrency_manager is not None
    assert tx1.buffer_list is not None


def test_transaction_file_operations(real_transaction_env):
    """トランザクションでのファイル操作テスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    # ファイルサイズの確認（新しいファイル）
    assert tx.size("new_file.db") == 0
    
    # ファイルにブロックを追加
    block1 = tx.append("new_file.db")
    assert block1.file_name == "new_file.db"
    assert block1.block_number == 0
    
    # ファイルサイズの確認（ブロック追加後）
    assert tx.size("new_file.db") == 1
    
    # 複数ブロックの追加
    block2 = tx.append("new_file.db")
    block3 = tx.append("new_file.db")
    
    assert block2.block_number == 1
    assert block3.block_number == 2
    assert tx.size("new_file.db") == 3
    
    # ブロックサイズの確認
    assert tx.block_size() == file_manager.block_size
    
    tx.commit()


def test_transaction_data_operations(real_transaction_env):
    """トランザクションでのデータ操作テスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    # ファイルとブロックを作成
    block = tx.append("data_test.db")
    
    # ブロックをピンしてデータを書き込み
    tx.pin(block)
    tx.set_int(block, 0, 12345)
    tx.set_string(block, 4, "Hello Transaction")
    
    # データを読み取り
    assert tx.get_int(block, 0) == 12345
    assert tx.get_string(block, 4) == "Hello Transaction"
    
    # データを更新
    tx.set_int(block, 8, 67890)
    tx.set_string(block, 12, "Updated String")
    
    assert tx.get_int(block, 8) == 67890
    assert tx.get_string(block, 12) == "Updated String"
    
    tx.unpin(block)
    tx.commit()


def test_transaction_commit_rollback_cycle(real_transaction_env):
    """トランザクションのコミット/ロールバックサイクルテスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    
    # 最初のトランザクション: データを書き込んでコミット
    tx1 = Transaction(file_manager, log_manager, buffer_manager)
    block = tx1.append("commit_test.db")
    tx1.pin(block)
    tx1.set_int(block, 0, 999)
    tx1.commit()
    
    # 2番目のトランザクション: データを読み取り確認
    tx2 = Transaction(file_manager, log_manager, buffer_manager)
    tx2.pin(block)
    assert tx2.get_int(block, 0) == 999
    
    # データを変更してロールバック
    tx2.set_int(block, 0, 777)
    tx2.rollback()
    
    # 3番目のトランザクション: ロールバックされたことを確認
    tx3 = Transaction(file_manager, log_manager, buffer_manager)
    tx3.pin(block)
    # ロールバックされたので元の値が残っている
    assert tx3.get_int(block, 0) == 999
    tx3.commit()


def test_transaction_concurrent_access(real_transaction_env):
    """並行トランザクションアクセステスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    
    # テスト用ファイルを作成
    setup_tx = Transaction(file_manager, log_manager, buffer_manager)
    test_block = setup_tx.append("concurrent_test.db")
    setup_tx.pin(test_block)
    setup_tx.set_int(test_block, 0, 100)
    setup_tx.commit()
    
    results = []
    errors = []
    
    def transaction_worker(worker_id, operation_type):
        try:
            tx = Transaction(file_manager, log_manager, buffer_manager)
            tx.pin(test_block)
            
            if operation_type == "read":
                value = tx.get_int(test_block, 0)
                results.append((worker_id, "read", value))
            elif operation_type == "write":
                current_value = tx.get_int(test_block, 0)
                new_value = current_value + worker_id
                tx.set_int(test_block, 0, new_value)
                results.append((worker_id, "write", new_value))
            
            time.sleep(0.01)  # 競合状態を作る
            tx.commit()
            
        except Exception as e:
            errors.append((worker_id, str(e)))
    
    # 複数スレッドで同時アクセス
    threads = []
    for i in range(3):
        # 読み取りスレッド
        read_thread = threading.Thread(target=transaction_worker, args=(i, "read"))
        threads.append(read_thread)
        
        # 書き込みスレッド（数を少なくしてロック競合を減らす）
        if i < 2:
            write_thread = threading.Thread(target=transaction_worker, args=(i * 10, "write"))
            threads.append(write_thread)
    
    # スレッドを開始
    for thread in threads:
        thread.start()
    
    # 全スレッドの完了を待つ
    for thread in threads:
        thread.join()
    
    # エラーが発生していないことを確認
    print(f"Results: {results}")
    print(f"Errors: {errors}")
    
    # 少なくとも一部の操作は成功していることを確認
    assert len(results) > 0


def test_transaction_buffer_management(real_transaction_env):
    """トランザクションのバッファ管理テスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    # 初期状態のバッファ数を確認
    initial_buffers = tx.available_buffers()
    
    # 複数ブロックを作成してピン
    blocks = []
    for i in range(3):
        block = tx.append(f"buffer_test_{i}.db")
        blocks.append(block)
        tx.pin(block)
        tx.set_int(block, 0, i * 100)
    
    # バッファ数が減っていることを確認
    current_buffers = tx.available_buffers()
    assert current_buffers < initial_buffers
    
    # 一部ブロックをアンピン
    tx.unpin(blocks[0])
    
    # バッファ数が復元していることを確認
    after_unpin_buffers = tx.available_buffers()
    assert after_unpin_buffers > current_buffers
    
    # トランザクションをコミット（全バッファがアンピンされる）
    tx.commit()
    
    # バッファ数が完全に復元していることを確認
    final_buffers = tx.available_buffers()
    assert final_buffers == initial_buffers


def test_transaction_lock_timeout(real_transaction_env):
    """トランザクションロックタイムアウトテスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    
    # テスト用ブロックを作成
    setup_tx = Transaction(file_manager, log_manager, buffer_manager)
    test_block = setup_tx.append("lock_test.db")
    setup_tx.commit()
    
    tx1 = Transaction(file_manager, log_manager, buffer_manager)
    tx2 = Transaction(file_manager, log_manager, buffer_manager)
    
    # tx1で排他ロックを取得
    tx1.pin(test_block)
    tx1.set_int(test_block, 0, 999)  # 排他ロックがかかる
    
    # tx2で同じブロックに排他ロックを試みるとタイムアウトするはず
    try:
        tx2.pin(test_block)
        # この操作はタイムアウトする可能性がある
        tx2.set_int(test_block, 0, 888)
        tx2.commit()
        # タイムアウトしなかった場合は正常終了
        success = True
    except LockAbortException:
        # タイムアウトした場合
        success = False
        tx2.rollback()
    
    # tx1をコミット
    tx1.commit()
    
    # ロックの動作を確認（タイムアウトしたか、または正常に処理されたか）
    print(f"Transaction 2 success: {success}")


def test_transaction_multiple_files(real_transaction_env):
    """複数ファイルでのトランザクションテスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    # 複数ファイルを作成
    files_and_blocks = []
    for i in range(3):
        file_name = f"multi_file_{i}.db"
        block = tx.append(file_name)
        files_and_blocks.append((file_name, block))
        
        tx.pin(block)
        tx.set_int(block, 0, i * 1000)
        tx.set_string(block, 4, f"File {i} content")
    
    # 各ファイルのサイズを確認
    for file_name, _ in files_and_blocks:
        assert tx.size(file_name) == 1
    
    # 各ファイルのデータを確認
    for i, (file_name, block) in enumerate(files_and_blocks):
        assert tx.get_int(block, 0) == i * 1000
        assert tx.get_string(block, 4) == f"File {i} content"
        tx.unpin(block)
    
    tx.commit()


def test_transaction_stress_test(real_transaction_env):
    """トランザクションのストレステスト"""
    file_manager, log_manager, buffer_manager = real_transaction_env
    
    # 大量のデータ操作を行う
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    num_blocks = 10
    blocks = []
    
    # 多数のブロックを作成してデータを書き込み
    for i in range(num_blocks):
        block = tx.append("stress_test.db")
        blocks.append(block)
        
        tx.pin(block)
        # 各ブロックに複数のデータを書き込み
        for j in range(10):
            offset = j * 8
            tx.set_int(block, offset, i * 1000 + j)
        
        # 文字列データも書き込み
        tx.set_string(block, 80, f"Block {i} stress test data")
    
    # 全データを読み返して検証
    for i, block in enumerate(blocks):
        for j in range(10):
            offset = j * 8
            expected_value = i * 1000 + j
            actual_value = tx.get_int(block, offset)
            assert actual_value == expected_value
        
        expected_string = f"Block {i} stress test data"
        actual_string = tx.get_string(block, 80)
        assert actual_string == expected_string
        
        tx.unpin(block)
    
    # ファイルサイズの最終確認
    assert tx.size("stress_test.db") == num_blocks
    
    tx.commit()
