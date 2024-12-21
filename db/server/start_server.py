from typing import Dict, Any


class StartServer:
    """データベースを初期化するクラス"""

    def __init__(self, db_name: str) -> None:
        """データベースを初期化
        :param db_name: データベース名(Noneの場合はメモリ上に作成)
        """
        if db_name is None or db_name == ":memory:":
            self.db_name = ":memory:"
            self.storage: Dict[str, Any] = {}
            print("Using in-memory database")
        else:
            self.db_name = db_name
            # TODO: 後で適切なデータベースを選択する
            self.storage = {}
            print(f"Using database {db_name}")
