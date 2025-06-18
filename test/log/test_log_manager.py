import shutil
import tempfile

import pytest

from db.file.file_manager import FileManager
from db.log.log_manager import LogManager


@pytest.fixture
def temp_log_env():
    temp_dir = tempfile.mkdtemp()
    block_size = 1024
    file_manager = FileManager(temp_dir, block_size)
    log_file = "test_log"
    log_manager = LogManager(file_manager, log_file)

    yield log_manager, file_manager, log_file

    shutil.rmtree(temp_dir)


def test_append_increases_lsn(temp_log_env):
    log_manager, *_ = temp_log_env
    initial_lsn = log_manager.current_lsn
    lsn = log_manager.append(b"test record")
    assert lsn == initial_lsn + 1


def test_flush_writes_to_disk(temp_log_env):
    log_manager, file_manager, log_file = temp_log_env
    log_manager.append(b"test record")
    lsn = log_manager.current_lsn
    log_manager.flush(lsn)

    # 明示的な flush によって last_saved_lsn が更新されていることを確認
    assert log_manager.last_saved_lsn == lsn


def test_append_new_block_if_not_enough_space(temp_log_env):
    log_manager, file_manager, log_file = temp_log_env

    large_record = b"x" * (file_manager.block_size - 8)
    log_manager.append(large_record)

    prev_block = log_manager.current_block
    log_manager.append(b"tiny")
    new_block = log_manager.current_block

    assert prev_block != new_block


def test_log_manager_initialization_with_empty_file(temp_log_env):
    """空のログファイルでの初期化テスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    # 新しいログファイルの場合、初期状態を確認
    assert log_manager.current_lsn == 0
    assert log_manager.last_saved_lsn == 0
    assert log_manager.current_block is not None
    assert log_manager.current_block.file_name == log_file
    assert log_manager.current_block.block_number == 0


def test_log_manager_initialization_with_existing_file():
    """既存のログファイルでの初期化テスト"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_file = "existing_log"
        
        # 最初のログマネージャーでデータを書き込み
        log_manager1 = LogManager(file_manager, log_file)
        log_manager1.append(b"initial record")
        log_manager1.flush(log_manager1.current_lsn)
        
        # 新しいログマネージャーで既存ファイルを開く
        log_manager2 = LogManager(file_manager, log_file)
        
        # 既存ファイルの最後のブロックに移動していることを確認
        assert log_manager2.current_block is not None
        assert log_manager2.current_block.file_name == log_file
        
    finally:
        shutil.rmtree(temp_dir)


def test_multiple_record_append_and_lsn_increment(temp_log_env):
    """複数レコードの追加とLSNの増分テスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    records = [b"record1", b"record2", b"record3", b"longer record with more data"]
    lsns = []
    
    for record in records:
        lsn = log_manager.append(record)
        lsns.append(lsn)
    
    # LSNが順次増加していることを確認
    for i in range(1, len(lsns)):
        assert lsns[i] == lsns[i-1] + 1
    
    # 最終LSNが正しく設定されていることを確認
    assert log_manager.current_lsn == lsns[-1]


def test_flush_with_lower_lsn_does_not_flush(temp_log_env):
    """低いLSNでのflushが実際にはflushしないことを確認"""
    log_manager, file_manager, log_file = temp_log_env
    
    # レコードを追加
    lsn1 = log_manager.append(b"record1")
    lsn2 = log_manager.append(b"record2")
    
    # 最初のflush
    log_manager.flush(lsn2)
    initial_saved_lsn = log_manager.last_saved_lsn
    
    # より低いLSNでflushを試行
    log_manager.flush(lsn1)
    
    # last_saved_lsnが変更されていないことを確認
    assert log_manager.last_saved_lsn == initial_saved_lsn


def test_log_manager_with_various_record_sizes(temp_log_env):
    """様々なサイズのレコードでのテスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    # 様々なサイズのレコード
    test_records = [
        b"",  # 空のレコード
        b"x",  # 1バイト
        b"small record",  # 小さいレコード
        b"x" * 100,  # 中サイズのレコード
        b"x" * 500,  # 大きめのレコード
    ]
    
    lsns = []
    for record in test_records:
        lsn = log_manager.append(record)
        lsns.append(lsn)
        
        # 各レコードが正しくLSNを増加させていることを確認
        assert lsn > 0
    
    # 全てのLSNが異なることを確認
    assert len(set(lsns)) == len(lsns)


def test_log_manager_boundary_conditions(temp_log_env):
    """境界条件のテスト"""
    from db.constants import ByteSize
    log_manager, file_manager, log_file = temp_log_env
    
    # ブロックサイズぎりぎりまでデータを埋める
    block_size = file_manager.block_size
    
    # 最初のブロックの境界位置を取得
    initial_boundary = log_manager.log_page.get_int(0)
    
    # ブロックサイズ - ヘッダサイズ - レコードサイズぎりぎりのレコード
    # ByteSize.Int（4バイト）はレコード長情報用
    max_record_size = initial_boundary - ByteSize.Int - ByteSize.Int
    large_record = b"x" * max_record_size
    
    # 大きなレコードを追加
    lsn1 = log_manager.append(large_record)
    assert lsn1 > 0
    
    # もう一つレコードを追加すると新しいブロックが作成される
    current_block_before = log_manager.current_block
    lsn2 = log_manager.append(b"next record")
    current_block_after = log_manager.current_block
    
    assert current_block_before != current_block_after
    assert lsn2 == lsn1 + 1


def test_log_manager_iterator_creation(temp_log_env):
    """LogIterator作成のテスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    # レコードを追加
    log_manager.append(b"test record for iterator")
    
    # イテレーターを作成
    iterator = log_manager.iterator()
    
    # イテレーターが正しく作成されることを確認
    assert iterator is not None
    assert iterator.file_manager == file_manager
    assert iterator.block == log_manager.current_block


def test_log_manager_with_zero_size_records(temp_log_env):
    """ゼロサイズレコードのテスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    # 空のレコードを複数追加
    empty_records_count = 10
    lsns = []
    
    for i in range(empty_records_count):
        lsn = log_manager.append(b"")
        lsns.append(lsn)
    
    # 空のレコードでもLSNが正しく増加することを確認
    assert len(lsns) == empty_records_count
    for i in range(1, len(lsns)):
        assert lsns[i] == lsns[i-1] + 1


def test_log_manager_flush_edge_cases(temp_log_env):
    """flush処理のエッジケースのテスト"""
    log_manager, file_manager, log_file = temp_log_env
    
    # レコード追加前の状態でflushを呼び出し
    initial_lsn = log_manager.current_lsn
    log_manager.flush(initial_lsn)
    assert log_manager.last_saved_lsn == initial_lsn
    
    # レコードを追加
    lsn = log_manager.append(b"test record")
    
    # 現在のLSNより大きい値でflush
    future_lsn = lsn + 100
    log_manager.flush(future_lsn)
    assert log_manager.last_saved_lsn == lsn


def test_log_manager_stress_test(temp_log_env):
    """ストレステスト（大量レコード）"""
    log_manager, file_manager, log_file = temp_log_env
    
    # 大量のレコードを追加
    num_records = 1000
    record_template = "Record number {}: some data"
    
    lsns = []
    for i in range(num_records):
        record_data = record_template.format(i).encode('utf-8')
        lsn = log_manager.append(record_data)
        lsns.append(lsn)
        
        # 10レコードごとにflush
        if i % 10 == 9:
            log_manager.flush(lsn)
    
    # 全てのLSNが順次増加していることを確認
    assert len(lsns) == num_records
    for i in range(1, len(lsns)):
        assert lsns[i] == lsns[i-1] + 1
    
    # 最終flush
    log_manager.flush(lsns[-1])
    assert log_manager.last_saved_lsn == lsns[-1]
