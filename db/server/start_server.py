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
            tx = db.new_transaction()

            create_table_sql = "CREATE TABLE test (id INT)"
            print(f"Executing: {create_table_sql}")
            planner.execute_update(create_table_sql, tx)
            tx.commit()

            tx = db.new_transaction()
            insert_sql = "INSERT INTO test (id) VALUES (1)"
            print(f"Executing: {insert_sql}")
            planner.execute_update(insert_sql, tx)
            tx.commit()

            select_sql = "SELECT id FROM test"
            print(f"Executing: {select_sql}")
            plan = planner.create_query_plan(select_sql, tx)
            scan = plan.open()

            while scan.next():
                print(f"id = {scan.get_int('id')}")

            scan.close()
            tx.commit()

        except KeyboardInterrupt:
            print("Server stopped")
            sys.exit(0)


if __name__ == "__main__":
    StartServer.main()
