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
            if planner is not None:
                tx = db.new_transaction()

                create_table_sql = "CREATE TABLE test (id varchar(10))"
                print(f"Executing: {create_table_sql}")
                planner.execute_update(create_table_sql, tx)
                tx.commit()

                tx2 = db.new_transaction()
                insert_sql = "INSERT INTO test (id) VALUES ('hello')"
                print(f"Executing: {insert_sql}")
                planner.execute_update(insert_sql, tx2)
                tx2.commit()

                tx2 = db.new_transaction()
                insert_sql = "INSERT INTO test (id) VALUES ('python')"
                print(f"Executing: {insert_sql}")
                planner.execute_update(insert_sql, tx2)
                tx2.commit()

                tx3 = db.new_transaction()
                select_sql = "SELECT id FROM test"
                print(f"Executing: {select_sql}")
                plan = planner.create_query_plan(select_sql, tx3)
                scan = plan.open()

                while scan.next():
                    print(f"id = {scan.get_string('id')}")

                scan.close()
                tx3.commit()

                tx4 = db.new_transaction()
                update_sql = "UPDATE test SET id = 'world' WHERE id = 'hello'"
                print(f"Executing: {update_sql}")
                planner.execute_update(update_sql, tx4)
                tx4.commit()

                tx5 = db.new_transaction()
                select_sql = "SELECT id FROM test"
                print(f"Executing: {select_sql}")
                plan = planner.create_query_plan(select_sql, tx5)
                scan = plan.open()

                while scan.next():
                    print(f"id = {scan.get_string('id')}")

                scan.close()
                tx5.commit()

                tx6 = db.new_transaction()
                delete_sql = "DELETE FROM test WHERE id = 'world'"
                print(f"Executing: {delete_sql}")
                planner.execute_update(delete_sql, tx6)
                tx6.commit()

                tx5 = db.new_transaction()
                select_sql = "SELECT id FROM test"
                print(f"Executing33: {select_sql}")
                plan = planner.create_query_plan(select_sql, tx5)
                scan = plan.open()

                while scan.next():
                    print(f"id = {scan.get_string('id')}")

                scan.close()
                tx5.commit()

                # tx4 = db.new_transaction()
                # delete_sql = "DELETE FROM test"
                # print(f"Executing: {delete_sql}")
                # planner.execute_update(delete_sql, tx4)
                # tx4.commit()
                #
                # tx5 = db.new_transaction()
                # select_sql = "SELECT id FROM test"
                # print(f"Executing: {select_sql}")
                # plan = planner.create_query_plan(select_sql, tx5)
                # scan = plan.open()
                #
                # while scan.next():
                #     print(f"id = {scan.get_int('id')}")
                #
                # scan.close()
                # tx5.commit()

        except KeyboardInterrupt:
            print("Server stopped")
            sys.exit(0)


if __name__ == "__main__":
    StartServer.main()
