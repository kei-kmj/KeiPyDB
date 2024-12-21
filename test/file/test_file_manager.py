from db.file.file_manager import FileManager


def setup_test_directory(tmp_path):
    test_dir = tmp_path / "test_db"
    test_dir.mkdir()
    return test_dir


def test_一時ファイルが削除されること(tmp_path):
    db_directory = setup_test_directory(tmp_path)
    temp_file = db_directory / "tempfile"
    temp_file.touch()  # Create a temporary file

    block_size = 1024
    file_mgr = FileManager(db_directory, block_size)

    assert not temp_file.exists()

    file_mgr.close()


def test_ディレクトリが新しいかどうかの判定(tmp_path):
    db_directory = tmp_path / "new_db"
    block_size = 1024
    file_mgr = FileManager(db_directory, block_size)

    assert file_mgr.is_new

    file_mgr = FileManager(db_directory, block_size)

    assert not file_mgr.is_new

    file_mgr.close()
