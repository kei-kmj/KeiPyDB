import os
from pathlib import Path
from typing import BinaryIO, Dict, cast

from db.constants import FileMode
from db.file.block_id import BlockID
from db.file.page import Page


class FileManager:
    def __init__(self, db_directory: str | Path, block_size: int):
        """ファイルを管理するクラス"""
        self.db_directory: Path = Path(db_directory)
        self.block_size: int = block_size
        self.is_new: bool = not self.db_directory.exists()
        self.open_files: Dict[str, BinaryIO] = {}

        if self.is_new:
            self.db_directory.mkdir(parents=True, exist_ok=True)

        # 一時ファイルを削除
        for file in self.db_directory.iterdir():
            if file.name.startswith("temp"):
                file.unlink()

    def read(self, block_id: BlockID, page: Page) -> None:
        """ブロックIDに対応するファイルからデータを読み込む"""
        if block_id.number() < 0:
            raise ValueError(f"Invalid block number: {block_id.number()}")

        try:
            f = self._get_file(block_id.file_name)
            f.seek(block_id.number() * self.block_size)
            page.set_bytes(0, f.read(self.block_size))

        except Exception as e:
            raise RuntimeError(f"Cannot read block {block_id} from file: {e}")

    def write(self, block: BlockID, page: Page) -> None:
        """ブロックIDに対応するファイルにデータを書き込む"""
        try:
            f = self._get_file(block.file_name)
            f.seek(block.block_number * self.block_size)
            f.write(page.get_contents())
            f.flush()

        except Exception as e:
            raise RuntimeError(f"Cannot write block {block} to file: {e}")

    def append(self, file_name: str) -> BlockID:
        """ファイルに新しいブロックを追加して、そのブロックIDを返す"""
        try:
            new_block_number = self.length(file_name)
            block = BlockID(file_name, new_block_number)

            f = self._get_file(file_name)
            f.seek(block.block_number * self.block_size)

            empty_data = b"\x00" * self.block_size
            f.write(empty_data)
            f.flush()
            return block

        except Exception as e:
            raise RuntimeError(f"Cannot append block to file {file_name}: {e}")

    def length(self, file_name: str) -> int:
        """ファイルのブロック数を返す"""
        try:
            f = self._get_file(file_name)
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            return file_size // self.block_size
        except Exception as e:
            raise RuntimeError(f"Cannot get length of file {file_name}: {e}")

    def _get_file(self, file_name: str) -> BinaryIO:
        """ファイルを取得する"""

        if file_name in self.open_files:
            return self.open_files[file_name]

        file_path = self.db_directory / file_name

        if file_name not in self.open_files:
            mode = FileMode.ReadWrite if file_path.exists() else FileMode.WriteNew

            self.open_files[file_name] = cast(BinaryIO, open(file_path, mode))

        return self.open_files[file_name]
