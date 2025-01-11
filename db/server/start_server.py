import sys
import threading

from db.server.keipy_db import KeiPyDB


class StartServer:
    stop_event = threading.Event()

    @staticmethod
    def main() -> None:
        """データベースを初期化する"""
        dir_name = sys.argv[1] if len(sys.argv) > 1 else "data"
        db = KeiPyDB(dir_name)

        print("Database server ready")
        # シグナルハンドラの登録

        try:
            planner = db.get_planner()

            create_table_sql = "CREATE TABLE test (id INT, name VARCHAR(50)"
            print(f"Executing: {create_table_sql}")
            planner.execute_update(create_table_sql, db.new_transaction())

        except KeyboardInterrupt:
            print("Server stopped")
            sys.exit(0)


if __name__ == "__main__":
    StartServer.main()
