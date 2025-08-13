from typing_extensions import Optional

from db.buffer.buffer_manager import BufferManager
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.metadata.metadata_manager import MetadataManager
from db.plan.basic_query_planner import BasicQueryPlanner
from db.plan.basic_update_planner import BasicUpdatePlanner
from db.plan.planner import Planner
from db.transaction.transaction import Transaction


class KeiPyDB:
    BLOCK_SIZE = 400
    BUFFER_SIZE = 8
    LOG_FILE = "keipydb.log"

    def __init__(self, dir_name: str, block_size: int = BLOCK_SIZE, buffer_size: int = BUFFER_SIZE) -> None:
        try:
            self.file_manager = FileManager(dir_name, block_size)
            self.log_manager = LogManager(self.file_manager, KeiPyDB.LOG_FILE)
            self.buffer_manager = BufferManager(self.file_manager, self.log_manager, buffer_size)

            is_new = self.file_manager.is_new
            self.metadata_manager = None
            self.planner = None

            if is_new:
                print("creating new database")
            else:
                print("recovering existing database")

            transaction = self.new_transaction()
            if not is_new:
                transaction.recover()

            self.metadata_manager = MetadataManager(is_new, transaction)

            self.query_planner = BasicQueryPlanner(self.metadata_manager)
            self.update_planner = BasicUpdatePlanner(self.metadata_manager)

            self.planner = Planner(self.query_planner, self.update_planner)

            transaction.commit()

        except (OSError, IOError) as e:
            # ファイルアクセスエラー
            raise RuntimeError(f"データベースファイルアクセスエラー: {e}") from e
        except PermissionError as e:
            # 権限エラー
            raise RuntimeError(f"データベースディレクトリの権限が不足: {e}") from e
        except ValueError as e:
            # 設定値エラー
            raise RuntimeError(f"データベース設定値エラー: {e}") from e
        except Exception as e:
            # その他の予期しないエラー
            raise RuntimeError(f"データベース初期化に失敗しました: {e}") from e

    def new_transaction(self) -> Transaction:
        return Transaction(self.file_manager, self.log_manager, self.buffer_manager)

    def get_metadata_manager(self) -> Optional[MetadataManager]:
        return self.metadata_manager

    def get_planner(self) -> Optional[Planner]:
        return self.planner

    def get_file_manager(self) -> FileManager:
        return self.file_manager

    def get_log_manager(self) -> LogManager:
        return self.log_manager

    def get_buffer_manager(self) -> BufferManager:
        return self.buffer_manager
