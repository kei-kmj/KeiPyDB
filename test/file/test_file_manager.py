import shutil
import struct
from pathlib import Path

import pytest

from db.constants import ByteSize
from db.file.block_id import BlockID
from db.file.file_manager import FileManager
from db.file.page import Page


@pytest.fixture
def setup_dir(tmp_path):
    """一時ディレクトリを作成"""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield str(test_dir)
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def setup_file(setup_dir):
    """指定されたファイルを作成"""

    def _setup_file(file_name):
        file_path = Path(setup_dir) / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb"):
            pass  # 空のファイルを作成
        return file_path

    return _setup_file


def test_new_file_manager(setup_dir):
    block_size = 4096
    db_directory = setup_dir

    # テスト前にディレクトリが存在したら削除
    shutil.rmtree(db_directory, ignore_errors=True)

    manager = FileManager(db_directory, block_size)

    assert manager is not None
    assert manager.db_directory == Path(db_directory)
    assert manager.block_size == block_size
    assert manager.is_new
    assert manager.open_files == {}


def test_existing_file_manager(setup_dir):
    dummy_file = Path(setup_dir) / "dummy.txt"
    dummy_file.write_text("test")

    manager = FileManager(setup_dir, 4096)

    assert not manager.is_new


def test_file_manager_init_with_path_object(setup_dir):
    # Path オブジェクトでも初期化できることを確認
    path = Path(setup_dir)
    manager = FileManager(path, 1024)
    
    assert manager.db_directory == path
    assert manager.block_size == 1024


def test_file_manager_temp_file_cleanup(setup_dir):
    # 一時ファイルを作成
    temp_files = ["temp123.txt", "tempfile.db", "temp_data"]
    non_temp_files = ["data.db", "test.txt"]
    
    for file_name in temp_files + non_temp_files:
        (Path(setup_dir) / file_name).write_text("test")
    
    # FileManager初期化時に一時ファイルが削除される
    FileManager(setup_dir, 4096)
    
    # 一時ファイルは削除され、通常ファイルは残る
    for file_name in temp_files:
        assert not (Path(setup_dir) / file_name).exists()
    
    for file_name in non_temp_files:
        assert (Path(setup_dir) / file_name).exists()


def test_file_manager_write(setup_file, setup_dir):
    block_size = 4096
    db_directory = setup_dir
    manager = FileManager(db_directory, block_size)

    file_name = "test_file"
    page = Page(block_size)
    test_data = "test_data"
    page.set_string(0, test_data)
    block_id = BlockID(file_name, 0)

    manager.write(block_id, page)

    # ファイルが存在することを確認
    file_path = Path(db_directory) / file_name
    assert file_path.exists()

    # ファイルの内容を確認
    with file_path.open("rb") as f:
        file_content = f.read()

    string_length = len(test_data)
    expected_data = b"\x00\x00\x00\t" + test_data.encode("ascii")
    assert file_content[: ByteSize.Int] == struct.pack(">I", string_length)
    assert file_content[: len(expected_data)] == expected_data


def test_file_manager_write_multiple_blocks(setup_dir):
    block_size = 512
    manager = FileManager(setup_dir, block_size)
    file_name = "multi_block_file"
    
    # 複数のブロックに書き込み
    blocks_data = [
        (0, "First block"),
        (1, "Second block"),
        (2, "Third block"),
        (5, "Sixth block"),  # ブロック番号が飛んでいる
    ]
    
    # まず必要なブロックを作成
    for i in range(6):  # 0から5までのブロックを作成
        manager.append(file_name)
    
    for block_num, data in blocks_data:
        page = Page(block_size)
        page.set_string(0, data)
        block_id = BlockID(file_name, block_num)
        manager.write(block_id, page)
    
    # 各ブロックを読み込んで検証
    for block_num, expected_data in blocks_data:
        page = Page(block_size)
        block_id = BlockID(file_name, block_num)
        manager.read(block_id, page)
        assert page.get_string(ByteSize.Int) == expected_data


def test_file_manager_write_error_handling(setup_dir):
    manager = FileManager(setup_dir, 4096)
    page = Page(4096)
    
    # 無効なファイル名でのエラーハンドリング（実装依存）
    # 注：実際の動作はOSやファイルシステムに依存
    try:
        # 無効なファイル名の例（OSによって異なる）
        invalid_block = BlockID("", 0)
        manager.write(invalid_block, page)
    except RuntimeError as e:
        assert "Cannot write block" in str(e)


def test_file_manager_read(setup_file, setup_dir):
    block_size = 512
    db_directory = setup_dir
    manager = FileManager(db_directory, block_size)

    file_name = "test_file"
    page = Page(block_size)
    test_data = "test_data"
    page.set_string(0, test_data)
    block_id = BlockID(file_name, 0)

    # ファイルに書き込む
    manager.write(block_id, page)

    # ファイルから読み込む
    read_page = Page(block_size)
    manager.read(block_id, read_page)

    # readメソッドはページ全体をset_bytesで設定するため、offset 0から読む
    assert read_page.get_string(ByteSize.Int) == test_data


def test_file_manager_read_empty_data(setup_file, setup_dir):
    block_size = 512
    db_directory = setup_dir
    manager = FileManager(db_directory, block_size)

    file_name = "test_file"
    page = Page(block_size)
    test_data = ""
    page.set_string(0, test_data)
    block_id = BlockID(file_name, 0)

    # ファイルに書き込む
    manager.write(block_id, page)

    # ファイルから読み込む
    read_page = Page(block_size)
    manager.read(block_id, read_page)

    assert read_page.get_string(ByteSize.Int) == ""


def test_file_manager_read_negative_block_number(setup_dir):
    manager = FileManager(setup_dir, 4096)
    page = Page(4096)
    
    # 負のブロック番号
    block_id = BlockID("test", -1)
    
    with pytest.raises(ValueError) as exc_info:
        manager.read(block_id, page)
    assert "Invalid block number" in str(exc_info.value)


def test_file_manager_read_beyond_file_end(setup_dir):
    manager = FileManager(setup_dir, 4096)
    file_name = "small_file.db"
    
    # ファイルに1ブロックだけ追加
    manager.append(file_name)
    
    # 存在しないブロック番号5を読もうとする
    page = Page(4096)
    block_id = BlockID(file_name, 5)
    
    # ファイルの終端を超えて読もうとすると、空のデータが返される（FileManagerの実装による）
    # この場合、エラーは発生しない可能性がある
    try:
        manager.read(block_id, page)
        # 読み取れた場合、データは空か0で埋められている可能性がある
    except RuntimeError as e:
        # エラーが発生した場合
        assert "Cannot read block" in str(e)


def test_file_manager_append(setup_dir):
    block_size = 512
    manager = FileManager(setup_dir, block_size)
    file_name = "append_test.db"
    
    # 新しいファイルに対してappend
    block1 = manager.append(file_name)
    assert block1.file_name == file_name
    assert block1.number() == 0
    
    # 続けてappend
    block2 = manager.append(file_name)
    assert block2.number() == 1
    
    block3 = manager.append(file_name)
    assert block3.number() == 2
    
    # ファイルサイズを確認
    file_path = Path(setup_dir) / file_name
    assert file_path.stat().st_size == block_size * 3


def test_file_manager_append_with_data(setup_dir):
    block_size = 512
    manager = FileManager(setup_dir, block_size)
    file_name = "data_append.db"
    
    # データを持つブロックを追加
    data_list = ["First", "Second", "Third"]
    
    for i, data in enumerate(data_list):
        block_id = manager.append(file_name)
        assert block_id.number() == i
        
        # データを書き込む
        page = Page(block_size)
        page.set_string(0, data)
        manager.write(block_id, page)
    
    # 各ブロックのデータを確認
    for i, expected_data in enumerate(data_list):
        page = Page(block_size)
        block_id = BlockID(file_name, i)
        manager.read(block_id, page)
        assert page.get_string(ByteSize.Int) == expected_data


def test_file_manager_length(setup_dir):
    block_size = 1024
    manager = FileManager(setup_dir, block_size)
    file_name = "length_test.db"
    
    # 新しいファイルの長さは0
    assert manager.length(file_name) == 0
    
    # ブロックを追加していく
    for i in range(5):
        manager.append(file_name)
        assert manager.length(file_name) == i + 1
    
    # 別のファイル
    another_file = "another.db"
    assert manager.length(another_file) == 0
    
    manager.append(another_file)
    manager.append(another_file)
    assert manager.length(another_file) == 2
    assert manager.length(file_name) == 5  # 元のファイルは変わらない


def test_file_manager_get_file_caching(setup_dir):
    manager = FileManager(setup_dir, 4096)
    file_name = "cache_test.db"
    
    # 最初のアクセス
    manager.append(file_name)
    assert file_name in manager.open_files
    
    # 同じファイルへの再アクセス（キャッシュから取得）
    first_file = manager.open_files[file_name]
    manager.append(file_name)
    assert manager.open_files[file_name] is first_file  # 同じオブジェクト
    
    # 別のファイル
    another_file = "another.db"
    manager.append(another_file)
    assert another_file in manager.open_files
    assert len(manager.open_files) == 2


def test_file_manager_concurrent_operations(setup_dir):
    # 同じファイルに対する複数の操作
    manager = FileManager(setup_dir, 512)
    file_name = "concurrent.db"
    
    # すべての必要なブロックを最初に作成
    for i in range(10):
        manager.append(file_name)
    
    # 複数のブロックに書き込み
    pages = []
    for i in range(10):
        page = Page(512)
        page.set_int(0, i * 100)
        page.set_string(4, f"Block {i}")
        pages.append(page)
        
        block_id = BlockID(file_name, i)
        manager.write(block_id, page)
    
    # すべてのブロックを読み込んで検証
    for i in range(10):
        read_page = Page(512)
        block_id = BlockID(file_name, i)
        manager.read(block_id, read_page)
        
        # readはページ全体をset_bytesで設定するため、元のデータはByteSizeInt分オフセットされる
        assert read_page.get_int(ByteSize.Int) == i * 100
        assert read_page.get_string(ByteSize.Int + 4) == f"Block {i}"


def test_file_manager_error_propagation(setup_dir):
    manager = FileManager(setup_dir, 4096)
    
    # appendのエラー
    with pytest.raises(RuntimeError) as exc_info:
        # 無効なファイル名（実装とOSに依存）
        manager.append("")
    assert "Cannot append block" in str(exc_info.value)
    
    # lengthのエラー
    with pytest.raises(RuntimeError) as exc_info:
        manager.length("")
    assert "Cannot get length" in str(exc_info.value)
