import pytest

from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page
from db.log.log_iterator import LogIterator


@pytest.fixture
def setup_file_manager(tmp_path):
    """一時ディレクトリとFileManagerをセットアップ"""

    def _setup(block_size):
        db_directory = tmp_path / "test_log_iterator"
        db_directory.mkdir()
        return FileManager(db_directory, block_size)

    return _setup


@pytest.mark.parametrize(
    "block_number, offset, expected",
    [
        (0, 15, True),
        (0, 16, False),
        (1, 0, True),
    ],
)
def test_log_iterator_has_next(block_number, offset, expected, setup_file_manager):
    block_size = 16
    file_manager = setup_file_manager(block_size)

    log_iterator = LogIterator(file_manager, BlockID("file", block_number))
    log_iterator.current_offset = offset

    assert log_iterator.has_next() == expected


def test_log_iterator_raises_value_error_on_invalid_block(setup_file_manager):
    block_size = 16
    file_manager = setup_file_manager(block_size)

    file_name = "empty_log"
    page = Page(block_size)

    page.set_int(0, block_size)
    file_manager.write(BlockID(file_name, 0), page)

    log_iterator = LogIterator(file_manager, BlockID(file_name, 0))
    log_iterator.current_offset = block_size

    with pytest.raises(ValueError, match="Block number must be non-negative: -1"):
        next(log_iterator)


def test_log_iterator_with_real_log_data():
    """実際のログデータでのイテレーターテスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 256
        file_manager = FileManager(temp_dir, block_size)
        
        # ログファイルを作成してデータを書き込み
        from db.log.log_manager import LogManager
        log_manager = LogManager(file_manager, "test_log")
        
        # テストデータを追加
        test_records = [
            b"First log record",
            b"Second log record with more data",
            b"Third record",
            b"Fourth and final record for this test"
        ]
        
        for record in test_records:
            log_manager.append(record)
        
        # ログをフラッシュ
        log_manager.flush(log_manager.current_lsn)
        
        # イテレーターでデータを読み取り
        iterator = log_manager.iterator()
        
        # 逆順でレコードが読み取れることを確認（ログは後方から読み取る）
        retrieved_records = []
        try:
            while True:
                record = next(iterator)
                retrieved_records.append(record)
        except StopIteration:
            pass
        
        # 逆順で取得されることを確認
        expected_reversed = list(reversed(test_records))
        assert retrieved_records == expected_reversed
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_move_to_block():
    """
move_to_blockメソッドのテスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 512
        file_manager = FileManager(temp_dir, block_size)
        
        # テスト用のブロックを作成
        page1 = Page(block_size)
        page2 = Page(block_size)
        
        # ブロック1: オフセットを100に設定
        page1.set_int(0, 100)
        page1.set_bytes(80, b"Block 1 data")
        
        # ブロック2: オフセットを200に設定
        page2.set_int(0, 200)
        page2.set_bytes(180, b"Block 2 data")
        
        # ファイルに書き込み
        file_name = "multi_block_test"
        file_manager.write(BlockID(file_name, 0), page1)
        file_manager.write(BlockID(file_name, 1), page2)
        
        # イテレーターを作成（ブロック1から開始）
        iterator = LogIterator(file_manager, BlockID(file_name, 0))
        assert iterator.current_offset == 100
        
        # ブロック2に移動
        iterator.move_to_block(BlockID(file_name, 1))
        assert iterator.current_offset == 200
        assert iterator.block.block_number == 1
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_cross_block_iteration():
    """複数ブロックをまたいだイテレーションテスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 128  # 小さいブロックサイズで複数ブロックを強制
        file_manager = FileManager(temp_dir, block_size)
        
        from db.log.log_manager import LogManager
        log_manager = LogManager(file_manager, "cross_block_test")
        
        # ブロックを跨ぐような大きなレコードを追加
        large_records = [
            b"x" * 50,  # ブロック1に収まる
            b"y" * 50,  # ブロック2に移動する可能性
            b"z" * 30,  # さらにブロックを跨ぐ可能性
        ]
        
        for record in large_records:
            log_manager.append(record)
        
        log_manager.flush(log_manager.current_lsn)
        
        # イテレーターで全レコードを読み取り
        iterator = log_manager.iterator()
        
        retrieved_records = []
        try:
            while True:
                record = next(iterator)
                retrieved_records.append(record)
        except StopIteration:
            pass
        
        # 逆順で全てのレコードが取得されることを確認
        expected_reversed = list(reversed(large_records))
        assert retrieved_records == expected_reversed
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_empty_log():
    """空のログでのイテレーターテスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 256
        file_manager = FileManager(temp_dir, block_size)
        
        from db.log.log_manager import LogManager
        log_manager = LogManager(file_manager, "empty_log_test")
        
        # レコードを追加せずにイテレーターを作成
        log_manager.flush(log_manager.current_lsn)
        iterator = log_manager.iterator()
        
        # レコードがないことを確認
        with pytest.raises(StopIteration):
            next(iterator)
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_single_record():
    """単一レコードでのイテレーターテスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 256
        file_manager = FileManager(temp_dir, block_size)
        
        from db.log.log_manager import LogManager
        log_manager = LogManager(file_manager, "single_record_test")
        
        # 単一レコードを追加
        test_record = b"Single test record"
        log_manager.append(test_record)
        log_manager.flush(log_manager.current_lsn)
        
        # イテレーターで読み取り
        iterator = log_manager.iterator()
        
        # 最初のレコードを取得
        first_record = next(iterator)
        assert first_record == test_record
        
        # 2番目のレコードは存在しない
        with pytest.raises(StopIteration):
            next(iterator)
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_has_next_edge_cases():
    """
has_nextメソッドのエッジケーステスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 128
        file_manager = FileManager(temp_dir, block_size)
        
        # 手動でブロックを作成
        page = Page(block_size)
        page.set_int(0, block_size)  # オフセットを最大値に設定
        
        file_name = "has_next_test"
        file_manager.write(BlockID(file_name, 0), page)
        
        # イテレーターを作成
        iterator = LogIterator(file_manager, BlockID(file_name, 0))
        
        # 最初の状態ではhas_nextはFalse（オフセットがブロックサイズと同じ）
        assert not iterator.has_next()
        
        # オフセットを変更
        iterator.current_offset = block_size - 1
        assert iterator.has_next()
        
        iterator.current_offset = 0
        assert iterator.has_next()
        
    finally:
        shutil.rmtree(temp_dir)


def test_log_iterator_boundary_conditions():
    """イテレーターの境界条件テスト"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 64  # 非常に小さいブロックサイズ
        file_manager = FileManager(temp_dir, block_size)
        
        from db.log.log_manager import LogManager
        log_manager = LogManager(file_manager, "boundary_test")
        
        # ブロックの容量を超えるサイズのレコード
        large_record = b"x" * (block_size - 10)  # ヘッダーを除いた最大サイズ
        
        log_manager.append(large_record)
        log_manager.flush(log_manager.current_lsn)
        
        # イテレーターで読み取り
        iterator = log_manager.iterator()
        retrieved_record = next(iterator)
        
        assert retrieved_record == large_record
        
        # 次のレコードは存在しない
        with pytest.raises(StopIteration):
            next(iterator)
        
    finally:
        shutil.rmtree(temp_dir)
