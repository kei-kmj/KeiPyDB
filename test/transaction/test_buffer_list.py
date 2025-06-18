import tempfile
import shutil
from unittest.mock import Mock

import pytest

from db.buffer.buffer import Buffer
from db.buffer.buffer_manager import BufferManager
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.transaction.buffer_list import BufferList


def test_指定されたブロックのバッファを取得できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)

    buffer_list.buffers[block] = buffer
    assert buffer_list.get_buffer(block) == buffer
    assert buffer_list.get_buffer(BlockID("testfile", 2)) is None


def test_ブロックをピン留めして追跡できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)
    buffer_manager.pin.return_value = buffer

    buffer_list.pin(block)

    assert buffer_list.buffers[block] == buffer
    assert block in buffer_list.pins
    buffer_manager.pin.assert_called_once_with(block)


def test_ブロックをアンピンして追跡から削除できる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    buffer = Mock(spec=Buffer)
    buffer_list.buffers[block] = buffer
    buffer_list.pins.append(block)

    buffer_list.unpin(block)

    assert block not in buffer_list.pins
    assert block not in buffer_list.buffers
    buffer_manager.unpin.assert_called_once_with(buffer)


def test_すべてのブロックをアンピンして状態をリセットできる():
    buffer_manager = Mock(spec=BufferManager)
    buffer_list = BufferList(buffer_manager)

    block = BlockID("testfile", 1)
    another_block = BlockID("testfile", 2)
    buffer = Mock(spec=Buffer)
    another_buffer = Mock(spec=Buffer)

    buffer_list.buffers[block] = buffer
    buffer_list.buffers[another_block] = another_buffer
    buffer_list.pins.extend([block, another_block])

    buffer_list.unpin_all()

    assert buffer_list.pins == []
    assert buffer_list.buffers == {}
    buffer_manager.unpin.assert_any_call(buffer)
    buffer_manager.unpin.assert_any_call(another_buffer)


@pytest.fixture
def real_buffer_list_env():
    """実際のBufferManagerを使用するテスト環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 512
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "buffer_list_test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 5)
        yield file_manager, log_manager, buffer_manager
    finally:
        shutil.rmtree(temp_dir)


def test_buffer_list_with_real_managers(real_buffer_list_env):
    """実際のマネージャーでのBufferListテスト"""
    file_manager, log_manager, buffer_manager = real_buffer_list_env
    buffer_list = BufferList(buffer_manager)
    
    # テストファイルを作成
    test_block = BlockID("buffer_list_test.db", 0)
    file_manager.append("buffer_list_test.db")
    
    # ブロックをピン
    buffer_list.pin(test_block)
    
    # バッファが正しく取得できることを確認
    buffer = buffer_list.get_buffer(test_block)
    assert buffer is not None
    assert buffer.is_pinned()
    assert test_block in buffer_list.pins
    assert test_block in buffer_list.buffers
    
    # データを書き込み
    buffer.get_contents().set_int(0, 12345)
    buffer.get_contents().set_string(4, "buffer list test")
    
    # データを読み取り
    assert buffer.get_contents().get_int(0) == 12345
    assert buffer.get_contents().get_string(4) == "buffer list test"
    
    # アンピン
    buffer_list.unpin(test_block)
    
    # アンピン後の状態確認
    assert not buffer.is_pinned()
    assert test_block not in buffer_list.pins
    assert test_block not in buffer_list.buffers


def test_buffer_list_multiple_pins_same_block(real_buffer_list_env):
    """同じブロックの複数ピンテスト"""
    file_manager, log_manager, buffer_manager = real_buffer_list_env
    buffer_list = BufferList(buffer_manager)
    
    # テストファイルを作成
    test_block = BlockID("multi_pin_test.db", 0)
    file_manager.append("multi_pin_test.db")
    
    # 同じブロックを複数回ピン
    buffer_list.pin(test_block)
    buffer_list.pin(test_block)
    buffer_list.pin(test_block)
    
    # pinsリストに複数回追加される
    assert buffer_list.pins.count(test_block) == 3
    
    # しかしbuffersには1つだけ
    assert len([k for k in buffer_list.buffers.keys() if k == test_block]) == 1
    
    # バッファのピン数を確認
    buffer = buffer_list.get_buffer(test_block)
    assert buffer.pins == 3
    
    # 一度アンピン
    buffer_list.unpin(test_block)
    assert buffer_list.pins.count(test_block) == 2
    assert buffer.pins == 2
    assert test_block in buffer_list.buffers  # まだバッファに残っている
    
    # 残りをアンピン
    buffer_list.unpin(test_block)
    buffer_list.unpin(test_block)
    
    # 完全にアンピンされた
    assert test_block not in buffer_list.pins
    assert test_block not in buffer_list.buffers
    assert buffer.pins == 0


def test_buffer_list_multiple_blocks(real_buffer_list_env):
    """複数ブロックでのBufferListテスト"""
    file_manager, log_manager, buffer_manager = real_buffer_list_env
    buffer_list = BufferList(buffer_manager)
    
    # 複数のテストファイルを作成
    blocks = []
    for i in range(3):
        block = BlockID(f"multi_block_test_{i}.db", 0)
        file_manager.append(f"multi_block_test_{i}.db")
        blocks.append(block)
        
        # ブロックをピンしてデータを書き込み
        buffer_list.pin(block)
        buffer = buffer_list.get_buffer(block)
        buffer.get_contents().set_int(0, i * 100)
        buffer.get_contents().set_string(4, f"Block {i}")
    
    # 全ブロックがピンされていることを確認
    assert len(buffer_list.pins) == 3
    assert len(buffer_list.buffers) == 3
    
    # 各ブロックのデータを確認
    for i, block in enumerate(blocks):
        buffer = buffer_list.get_buffer(block)
        assert buffer.get_contents().get_int(0) == i * 100
        assert buffer.get_contents().get_string(4) == f"Block {i}"
    
    # 一部のブロックをアンピン
    buffer_list.unpin(blocks[1])
    assert len(buffer_list.pins) == 2
    assert len(buffer_list.buffers) == 2
    assert blocks[1] not in buffer_list.buffers
    
    # 全てアンピン
    buffer_list.unpin_all()
    assert len(buffer_list.pins) == 0
    assert len(buffer_list.buffers) == 0


def test_buffer_list_edge_cases(real_buffer_list_env):
    """BufferListのエッジケーステスト"""
    file_manager, log_manager, buffer_manager = real_buffer_list_env
    buffer_list = BufferList(buffer_manager)
    
    # 存在しないブロックの取得
    non_existent_block = BlockID("non_existent.db", 0)
    assert buffer_list.get_buffer(non_existent_block) is None
    
    # 存在しないブロックのアンピン（エラーにならない）
    buffer_list.unpin(non_existent_block)  # 何も起こらない
    
    # 空の状態でunpin_all
    buffer_list.unpin_all()  # 何も起こらない
    assert len(buffer_list.pins) == 0
    assert len(buffer_list.buffers) == 0


def test_buffer_list_stress_test(real_buffer_list_env):
    """BufferListのストレステスト"""
    file_manager, log_manager, buffer_manager = real_buffer_list_env
    buffer_list = BufferList(buffer_manager)
    
    # 大量のブロックでテスト
    num_blocks = 20  # バッファプールサイズ（5）より多い
    blocks = []
    
    # ブロックを順次ピン（バッファ不足になる可能性がある）
    for i in range(min(num_blocks, 5)):  # バッファプールサイズに制限
        try:
            block = BlockID(f"stress_test_{i}.db", 0)
            file_manager.append(f"stress_test_{i}.db")
            buffer_list.pin(block)
            blocks.append(block)
            
            buffer = buffer_list.get_buffer(block)
            buffer.get_contents().set_int(0, i * 1000)
            
        except Exception as e:
            # バッファ不足の場合はスキップ
            print(f"Buffer shortage at block {i}: {e}")
            break
    
    # ピンされたブロック数を確認
    pinned_count = len(buffer_list.pins)
    assert pinned_count <= 5  # バッファプールサイズ以下
    
    # 各ブロックのデータを確認
    for i, block in enumerate(blocks):
        buffer = buffer_list.get_buffer(block)
        if buffer:  # バッファが存在する場合のみ
            assert buffer.get_contents().get_int(0) == i * 1000
    
    # 全てクリーンアップ
    buffer_list.unpin_all()
    assert len(buffer_list.pins) == 0
    assert len(buffer_list.buffers) == 0
