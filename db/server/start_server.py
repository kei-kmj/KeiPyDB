import sys
import threading

from db.server.keipy_db import KeiPyDB


class StartServer:
    stop_event = threading.Event()

    @staticmethod
    def main() -> None:
        """データベースを初期化する"""
        dir_name = sys.argv[1] if len(sys.argv) > 1 else "data"
        KeiPyDB(dir_name)

        print("Database server ready")


if __name__ == "__main__":
    StartServer.main()
