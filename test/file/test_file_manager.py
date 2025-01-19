import struct
from pathlib import Path
import shutil
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
    """指定されたファイルを作成"""
    def _setup_file(file_name):
        file_path = Path(setup_dir) / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as f:
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


def test_existing_file_manager(setup_dir):

    block_size = 4096
    db_directory = setup_dir

    # テスト前にディレクトリが存在することを確認
    assert Path(db_directory).exists()

    manager = FileManager(db_directory, block_size)

    assert manager is not None
    assert manager.db_directory == Path(db_directory)
    assert manager.block_size == block_size
    assert not manager.is_new


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
    expected_data = b'\x00\x00\x00\t' + test_data.encode("ascii")
    assert file_content[:ByteSize.Int] == struct.pack(">I", string_length)
    assert file_content[:len(expected_data)] == expected_data


def test_file_manager_read(setup_file, setup_dir):
    block_size = 13
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

    assert read_page.get_string(ByteSize.Int) == test_data


def test_file_manager_read_empty_data(setup_file, setup_dir):
    block_size = 13
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



