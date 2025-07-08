import shutil
import tempfile
from unittest.mock import Mock

import pytest

from db.buffer.buffer import Buffer
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp()
    block_size = 400
    file_manager = FileManager(temp_dir, block_size)
    log_manager = LogManager(file_manager, "test_log")
    buffer = Buffer(file_manager, log_manager)

    yield buffer, file_manager

    shutil.rmtree(temp_dir)


def test_pin_unpin_behavior(test_env):
    buffer, _ = test_env

    assert not buffer.is_pinned()
    buffer.pin()
    assert buffer.is_pinned()
    buffer.unpin()
    assert not buffer.is_pinned()


def test_modifying_tx_tracking(test_env):
    buffer, _ = test_env
    assert buffer.modifying_tx() == -1
    buffer.set_modified(transaction_number=42, log_sequence_number=7)
    assert buffer.modifying_tx() == 42


def test_flush_calls_log_and_file_write():
    mock_file_manager = Mock()
    mock_file_manager.block_size = 400
    mock_log_manager = Mock()
    buffer = Buffer(mock_file_manager, mock_log_manager)

    buffer.block = BlockID("test_file", 0)
    buffer.contents.set_int(4, 12345)
    buffer.set_modified(transaction_number=42, log_sequence_number=99)

    buffer.flush()

    mock_log_manager.flush.assert_called_once_with(99)
    mock_file_manager.write.assert_called_once_with(buffer.block, buffer.contents)
    assert buffer.transaction_number == -1


def test_buffer_initialization(test_env):
    """バッファの初期化テスト"""
    buffer, file_manager = test_env

    # 初期状態の確認
    assert buffer.pins == 0
    assert buffer.transaction_number == -1
    assert buffer.log_sequence_number == -1
    assert not buffer.is_pinned()
    assert buffer.modifying_tx() == -1
    assert len(buffer.contents.buffer) == file_manager.block_size


def test_assign_to_block_with_real_file(test_env):
    """実際のファイルでのassign_to_blockテスト"""
    buffer, file_manager = test_env

    # テストファイルを作成
    test_block = BlockID("test_file.db", 0)
    file_manager.append("test_file.db")  # ファイルを作成

    # データをファイルに書き込み
    from db.file.page import Page

    test_page = Page(file_manager.block_size)
    test_page.set_int(0, 12345)
    test_page.set_string(8, "test data")
    file_manager.write(test_block, test_page)

    # バッファにブロックを割り当て
    buffer.assign_to_block(test_block)

    # ブロックが正しく割り当てられていることを確認
    assert buffer.block == test_block
    assert buffer.pins == 0

    # ファイルからデータが正しく読み込まれていることを確認
    assert buffer.contents.get_int(0) == 12345
    assert buffer.contents.get_string(8) == "test data"


def test_multiple_pin_unpin_operations(test_env):
    """複数回のpin/unpin操作テスト"""
    buffer, _ = test_env

    # 複数回pin
    buffer.pin()
    buffer.pin()
    buffer.pin()

    assert buffer.pins == 3
    assert buffer.is_pinned()

    # 部分的にunpin
    buffer.unpin()
    assert buffer.pins == 2
    assert buffer.is_pinned()

    buffer.unpin()
    assert buffer.pins == 1
    assert buffer.is_pinned()

    # 最後のunpin
    buffer.unpin()
    assert buffer.pins == 0
    assert not buffer.is_pinned()


def test_set_modified_with_negative_lsn(test_env):
    """負のLSNでのset_modifiedテスト"""
    buffer, _ = test_env

    # 最初に正のLSNで設定
    buffer.set_modified(100, 50)
    assert buffer.transaction_number == 100
    assert buffer.log_sequence_number == 50

    # 負のLSNで設定（LSNは更新されない）
    buffer.set_modified(200, -1)
    assert buffer.transaction_number == 200
    assert buffer.log_sequence_number == 50  # 変更されない


def test_flush_without_modification(test_env):
    """変更なしでのflushテスト"""
    buffer, file_manager = test_env

    # ブロックを割り当てるが変更しない
    test_block = BlockID("unmodified_test.db", 0)
    file_manager.append("unmodified_test.db")
    buffer.assign_to_block(test_block)

    # 初期状態ではmodificationなし
    assert buffer.transaction_number == -1

    # flushしても何も起こらないことを確認
    buffer.flush()
    assert buffer.transaction_number == -1


def test_buffer_data_persistence(test_env):
    """バッファデータの永続化テスト"""
    buffer, file_manager = test_env

    # テストファイルを作成
    test_block = BlockID("persistence_test.db", 0)
    file_manager.append("persistence_test.db")

    # バッファにブロックを割り当ててデータを変更
    buffer.assign_to_block(test_block)
    buffer.contents.set_int(0, 999)
    buffer.contents.set_string(4, "persistent data")
    buffer.set_modified(500, 100)

    # フラッシュしてデータをファイルに書き込み
    buffer.flush()

    # 新しいバッファで同じブロックを読み込み
    new_buffer = Buffer(file_manager, buffer.log_manager)
    new_buffer.assign_to_block(test_block)

    # データが正しく永続化されていることを確認
    assert new_buffer.contents.get_int(0) == 999
    assert new_buffer.contents.get_string(4) == "persistent data"


def test_buffer_reassignment(test_env):
    """バッファの再割り当てテスト"""
    buffer, file_manager = test_env

    # 最初のブロックを作成して割り当て
    block1 = BlockID("reassign_test1.db", 0)
    file_manager.append("reassign_test1.db")
    buffer.assign_to_block(block1)
    buffer.contents.set_int(0, 111)
    buffer.set_modified(100, 50)

    # 2番目のブロックを作成
    block2 = BlockID("reassign_test2.db", 0)
    file_manager.append("reassign_test2.db")

    # ブロックの再割り当て（自動的に最初のブロックがフラッシュされる）
    buffer.assign_to_block(block2)

    # ブロックが変更されていることを確認
    assert buffer.block == block2
    assert buffer.pins == 0

    # 最初のブロックのデータがファイルに書き込まれていることを確認
    verification_buffer = Buffer(file_manager, buffer.log_manager)
    verification_buffer.assign_to_block(block1)
    assert verification_buffer.contents.get_int(0) == 111


def test_buffer_with_large_data(test_env):
    """大きなデータでのバッファテスト"""
    buffer, file_manager = test_env

    # テストファイルを作成
    test_block = BlockID("large_data_test.db", 0)
    file_manager.append("large_data_test.db")
    buffer.assign_to_block(test_block)

    # 大きなデータをバッファに書き込み
    large_string = "X" * 300  # ブロックサイズの大部分を使用
    buffer.contents.set_string(0, large_string)
    buffer.set_modified(999, 200)

    # フラッシュしてデータを永続化
    buffer.flush()

    # 新しいバッファでデータを読み込み
    new_buffer = Buffer(file_manager, buffer.log_manager)
    new_buffer.assign_to_block(test_block)

    # 大きなデータが正しく永続化されていることを確認
    assert new_buffer.contents.get_string(0) == large_string
