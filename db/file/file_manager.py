import os
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Dict, cast

from db.file.block_id import BlockID
from db.file.constants import FileModes
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
        with self._get_file(block_id.file_name) as f:
            f.seek(block_id.block_number * self.block_size)
            data = f.read(self.block_size)
            page.buffer = BytesIO(data)

    def write(self, block: BlockID, page: Page) -> None:
        """ブロックIDに対応するファイルにデータを書き込む"""
        with self._get_file(block.file_name) as f:
            f.seek(block.block_number * self.block_size)
            f.write(page.get_contents())

    def append(self, file_name: str) -> BlockID:
        """ファイルに新しいブロックを追加して、そのブロックIDを返す"""
        new_block_number = self.length(file_name)
        block_id = BlockID(file_name, new_block_number)
        empty_data = b"\x00" * self.block_size

        with self._get_file(file_name) as f:
            f.seek(new_block_number * self.block_size)
            f.write(empty_data)

        return block_id

    def length(self, file_name: str) -> int:
        """ファイルのブロック数を返す"""
        with self._get_file(file_name) as f:
            return f.seek(0, os.SEEK_END) // self.block_size

    def _get_file(self, file_name: str) -> BinaryIO:
        """ファイルを取得する"""
        file_path = self.db_directory / file_name
        if file_name not in self.open_files:
            mode = FileModes.ReadWrite if file_path.exists() else FileModes.WriteNew
            self.open_files[file_name] = cast(BinaryIO, open(file_path, mode))
        return self.open_files[file_name]

    def close(self) -> None:
        """ファイルを閉じる"""
        for file in self.open_files.values():
            file.close()
        self.open_files.clear()
