import tempfile
import shutil
import threading
import time
from unittest.mock import Mock

import pytest

from db.buffer.buffer_manager import BufferManager, BufferAbortException
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


def test_get_number_of_available_buffers():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    assert buffer_manager.available() == 3


def test_flush_modified_buffer():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)
    buffer = buffer_manager._choose_unpinned_buffer()
    buffer.assign_to_block(block)
    buffer.set_modified(42, 100)

    buffer_manager.flush_all(42)

    log_manager.flush.assert_called_once_with(100)
    file_manager.write.assert_called_once_with(block, buffer.contents)


def test_pin_block():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager.pin(block)

    assert buffer.block == block
    assert buffer.pins == 1


def test_unpin_block():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager.pin(block)
    buffer_manager.unpin(buffer)

    assert buffer.pins == 0
    assert buffer_manager.available() == 3


def test_fined_existing_buffer():
    file_manager = Mock(spec=FileManager)
    file_manager.block_size = 1024
    log_manager = Mock(spec=LogManager)
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers=3)

    block = BlockID("testfile", 1)

    buffer = buffer_manager._choose_unpinned_buffer()
    buffer.assign_to_block(block)

    found_buffer = buffer_manager._find_existing_buffer(block)

    assert found_buffer == buffer


@pytest.fixture
def real_buffer_env():
    """実際のFileManagerとLogManagerを使用するテスト環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 512
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_log")
        yield file_manager, log_manager
    finally:
        shutil.rmtree(temp_dir)


def test_buffer_manager_initialization_with_real_managers(real_buffer_env):
    """実際のマネージャーでの初期化テスト"""
    file_manager, log_manager = real_buffer_env
    
    num_buffers = 5
    buffer_manager = BufferManager(file_manager, log_manager, num_buffers)
    
    # 初期状態の確認
    assert buffer_manager.available() == num_buffers
    assert len(buffer_manager.buffer_pool) == num_buffers
    
    # 各バッファが正しく初期化されていることを確認
    for buffer in buffer_manager.buffer_pool:
        assert not buffer.is_pinned()
        assert buffer.modifying_tx() == -1


def test_pin_and_unpin_with_real_data(real_buffer_env):
    """実際のデータでのpin/unpinテスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 3)
    
    # テストファイルを作成
    test_block = BlockID("pin_test.db", 0)
    file_manager.append("pin_test.db")
    
    # ブロックをpin
    buffer = buffer_manager.pin(test_block)
    
    assert buffer.block == test_block
    assert buffer.is_pinned()
    assert buffer_manager.available() == 2  # 1つ使用中
    
    # バッファにデータを書き込み
    buffer.get_contents().set_int(0, 12345)
    buffer.get_contents().set_string(4, "test pin data")
    
    # unpin
    buffer_manager.unpin(buffer)
    
    assert not buffer.is_pinned()
    assert buffer_manager.available() == 3  # 全て利用可能


def test_multiple_blocks_pinning(real_buffer_env):
    """複数ブロックのpinテスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 3)
    
    # 複数のテストファイルを作成
    blocks = []
    buffers = []
    
    for i in range(3):
        block = BlockID(f"multi_test_{i}.db", 0)
        file_manager.append(f"multi_test_{i}.db")
        blocks.append(block)
        
        buffer = buffer_manager.pin(block)
        buffer.get_contents().set_int(0, i * 100)
        buffers.append(buffer)
    
    # 全てのバッファが使用中
    assert buffer_manager.available() == 0
    
    # 各バッファが正しいブロックに割り当てられていることを確認
    for i, (block, buffer) in enumerate(zip(blocks, buffers)):
        assert buffer.block == block
        assert buffer.get_contents().get_int(0) == i * 100
    
    # 全てunpin
    for buffer in buffers:
        buffer_manager.unpin(buffer)
    
    assert buffer_manager.available() == 3


def test_buffer_reuse_after_unpin(real_buffer_env):
    """
unpin後のバッファ再利用テスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 2)
    
    # 最初のブロック
    block1 = BlockID("reuse_test1.db", 0)
    file_manager.append("reuse_test1.db")
    buffer1 = buffer_manager.pin(block1)
    buffer1.get_contents().set_int(0, 111)
    
    # 2番目のブロック
    block2 = BlockID("reuse_test2.db", 0)
    file_manager.append("reuse_test2.db")
    buffer2 = buffer_manager.pin(block2)
    buffer2.get_contents().set_int(0, 222)
    
    # 全てのバッファが使用中
    assert buffer_manager.available() == 0
    
    # 1番目をunpin
    buffer_manager.unpin(buffer1)
    assert buffer_manager.available() == 1
    
    # 3番目のブロック（バッファが再利用される）
    block3 = BlockID("reuse_test3.db", 0)
    file_manager.append("reuse_test3.db")
    buffer3 = buffer_manager.pin(block3)
    
    # バッファが再利用されていることを確認
    assert buffer3.block == block3
    assert buffer_manager.available() == 0
    
    # クリーンアップ
    buffer_manager.unpin(buffer2)
    buffer_manager.unpin(buffer3)


def test_same_block_multiple_pins(real_buffer_env):
    """同じブロックの複数pinテスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 3)
    
    # テストファイルを作成
    test_block = BlockID("same_block_test.db", 0)
    file_manager.append("same_block_test.db")
    
    # 同じブロックを複数回pin
    buffer1 = buffer_manager.pin(test_block)
    buffer2 = buffer_manager.pin(test_block)
    buffer3 = buffer_manager.pin(test_block)
    
    # 全て同じバッファオブジェクトであることを確認
    assert buffer1 is buffer2 is buffer3
    assert buffer1.pins == 3
    assert buffer_manager.available() == 2  # 1つのバッファだけ使用中
    
    # 部分的にunpin
    buffer_manager.unpin(buffer1)
    assert buffer1.pins == 2
    assert buffer_manager.available() == 2  # まだpinned状態
    
    buffer_manager.unpin(buffer2)
    assert buffer1.pins == 1
    assert buffer_manager.available() == 2
    
    # 最後のunpin
    buffer_manager.unpin(buffer3)
    assert buffer1.pins == 0
    assert buffer_manager.available() == 3  # 全て利用可能


def test_flush_all_for_transaction(real_buffer_env):
    """特定トランザクションの全バッファフラッシュテスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 3)
    
    # 複数のブロックを作成して異なるトランザクションで変更
    blocks = []
    buffers = []
    
    for i in range(3):
        block = BlockID(f"flush_test_{i}.db", 0)
        file_manager.append(f"flush_test_{i}.db")
        blocks.append(block)
        
        buffer = buffer_manager.pin(block)
        buffer.get_contents().set_int(0, i * 1000)
        
        # トランザクション100または200で変更
        tx_num = 100 if i < 2 else 200
        buffer.set_modified(tx_num, i * 10)
        buffers.append(buffer)
    
    # トランザクション100のバッファだけをフラッシュ
    buffer_manager.flush_all(100)
    
    # トランザクション100のバッファはフラッシュされている
    assert buffers[0].modifying_tx() == -1
    assert buffers[1].modifying_tx() == -1
    
    # トランザクション200のバッファはフラッシュされていない
    assert buffers[2].modifying_tx() == 200
    
    # クリーンアップ
    for buffer in buffers:
        buffer_manager.unpin(buffer)


def test_buffer_abort_when_no_available_buffers(real_buffer_env):
    """バッファ不足時のアボートテスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 2)  # 小さいプール
    
    # 全てのバッファをpin
    blocks = []
    buffers = []
    
    for i in range(2):
        block = BlockID(f"abort_test_{i}.db", 0)
        file_manager.append(f"abort_test_{i}.db")
        blocks.append(block)
        
        buffer = buffer_manager.pin(block)
        buffers.append(buffer)
    
    assert buffer_manager.available() == 0
    
    # 新しいブロックをpinしようとするとタイムアウトでアボート
    new_block = BlockID("abort_test_new.db", 0)
    file_manager.append("abort_test_new.db")
    
    # タイムアウトを短くするためにMAX_TIMEを一時的に変更
    original_max_time = BufferManager.MAX_TIME
    BufferManager.MAX_TIME = 0.1  # 100ms
    
    try:
        with pytest.raises(BufferAbortException):
            buffer_manager.pin(new_block)
    finally:
        BufferManager.MAX_TIME = original_max_time
    
    # クリーンアップ
    for buffer in buffers:
        buffer_manager.unpin(buffer)


def test_concurrent_buffer_access(real_buffer_env):
    """並行バッファアクセステスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 3)
    
    # テストファイルを作成
    test_block = BlockID("concurrent_test.db", 0)
    file_manager.append("concurrent_test.db")
    
    results = []
    errors = []
    
    def pin_and_modify(thread_id):
        try:
            buffer = buffer_manager.pin(test_block)
            
            # データを変更
            current_value = buffer.get_contents().get_int(0)
            time.sleep(0.01)  # 競合状態を作る
            buffer.get_contents().set_int(0, current_value + thread_id)
            buffer.set_modified(thread_id, thread_id)
            
            results.append((thread_id, buffer.get_contents().get_int(0)))
            
            time.sleep(0.01)
            buffer_manager.unpin(buffer)
            
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    # 複数スレッドで同時アクセス
    threads = []
    for i in range(5):
        thread = threading.Thread(target=pin_and_modify, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 全スレッドの完了を待つ
    for thread in threads:
        thread.join()
    
    # エラーが発生していないことを確認
    assert len(errors) == 0, f"Errors occurred: {errors}"
    
    # 結果が正しく記録されていることを確認
    assert len(results) == 5


def test_buffer_manager_stress_test(real_buffer_env):
    """バッファマネージャーのストレステスト"""
    file_manager, log_manager = real_buffer_env
    buffer_manager = BufferManager(file_manager, log_manager, 5)
    
    # 大量のブロックに対してpin/unpinを繰り返す
    num_operations = 100
    num_blocks = 20  # バッファ数より多いブロック
    
    # テストファイルを作成
    blocks = []
    for i in range(num_blocks):
        block = BlockID(f"stress_test_{i}.db", 0)
        file_manager.append(f"stress_test_{i}.db")
        blocks.append(block)
    
    import random
    
    # ランダムにpin/unpinを繰り返す
    pinned_buffers = {}
    
    for operation in range(num_operations):
        if random.random() < 0.7 and len(pinned_buffers) < 5:  # 70%の確率でpin
            block = random.choice(blocks)
            if block not in pinned_buffers:
                try:
                    buffer = buffer_manager.pin(block)
                    buffer.get_contents().set_int(0, operation)
                    pinned_buffers[block] = buffer
                except BufferAbortException:
                    pass  # バッファ不足の場合はスキップ
        
        elif pinned_buffers:  # 30%の確率でunpin
            block = random.choice(list(pinned_buffers.keys()))
            buffer = pinned_buffers.pop(block)
            buffer_manager.unpin(buffer)
    
    # 残っているバッファをクリーンアップ
    for buffer in pinned_buffers.values():
        buffer_manager.unpin(buffer)
    
    # 最終状態の確認
    assert buffer_manager.available() == 5
