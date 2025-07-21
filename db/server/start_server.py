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

                create_table_sql2 = "CREATE TABLE sample (id varchar(10))"
                print(f"Executing: {create_table_sql2}")
                planner.execute_update(create_table_sql2, tx2)
                tx2.commit()

                tx_insert = db.new_transaction()
                insert_sql = "INSERT INTO test (id) VALUES ('001')"
                print(f"Executing: {insert_sql}")
                rows_affected = planner.execute_update(insert_sql, tx_insert)
                print(f"Rows affected: {rows_affected}")
                tx_insert.commit()

                tx_insert2 = db.new_transaction()
                insert_sql2 = "INSERT INTO test (id) VALUES ('002')"
                print(f"Executing: {insert_sql2}")
                rows_affected = planner.execute_update(insert_sql2, tx_insert2)
                print(f"Rows affected: {rows_affected}")
                tx_insert2.commit()

                tx_sample = db.new_transaction()
                insert_sample = "INSERT INTO sample (id) VALUES ('S001')"
                print(f"Executing: {insert_sample}")
                planner.execute_update(insert_sample, tx_sample)
                tx_sample.commit()

                # SELECT文を実行
                tx3 = db.new_transaction()
                select_sql = "SELECT id FROM test"
                print(f"Executing: {select_sql}")
                plan = planner.create_query_plan(select_sql, tx3)
                scan = plan.open()

                # 結果を表示
                while scan.next():
                    print(f"id = {scan.get_string('id')}")

                select_sql_s = "SELECT id FROM sample"
                print(f"Executing: {select_sql_s}")
                plan_s = planner.create_query_plan(select_sql_s, tx3)
                scan_s = plan_s.open()

                # 結果を表示
                while scan_s.next():
                    print(f"id = {scan_s.get_string('id')}")

                tx3.commit()

                tx_join = db.new_transaction()
                join_sql = "SELECT id FROM test, sample"
                print(f"Executing: {join_sql}")

                plan_join = planner.create_query_plan(join_sql, tx_join)
                scan_join = plan_join.open()

                print("Cross join results:")
                record_count = 0
                while scan_join.next():
                    record_count += 1
                    print(f"Record {record_count}:")

                    # testテーブルのid（ProductScanで優先される）
                    test_id = scan_join.get_string('id')
                    print(f"  id (from test): {test_id}")

                    # sampleテーブルのidを取得する試み
                    try:
                        # ProductPlanのschemaメソッドによると、重複時は'right_id'になるはず
                        sample_id = scan_join.get_string('right_id')
                        print(f"  right_id (from sample): {sample_id}")
                    except Exception as e:
                        print(f"  Cannot get right_id: {e}")

                    # 利用可能なフィールドを確認
                    if hasattr(scan_join, 'has_field'):
                        print(f"  Has 'id': {scan_join.has_field('id')}")
                        print(f"  Has 'right_id': {scan_join.has_field('right_id')}")

                scan_join.close()
                tx_join.commit()

                print(f"\nTotal records: {record_count}")






                # tx2 = db.new_transaction()
                # insert_sql = "INSERT INTO test (id) VALUES ('hello')"
                # print(f"Executing: {insert_sql}")
                # planner.execute_update(insert_sql, tx2)
                # tx2.commit()
                #
                # tx2 = db.new_transaction()
                # insert_sql = "INSERT INTO test (id) VALUES ('python')"
                # print(f"Executing: {insert_sql}")
                # planner.execute_update(insert_sql, tx2)
                # tx2.commit()
                #
                # tx3 = db.new_transaction()
                # select_sql = "SELECT id FROM test"
                # print(f"Executing: {select_sql}")
                # plan = planner.create_query_plan(select_sql, tx3)
                # scan = plan.open()
                #
                # while scan.next():
                #     print(f"id = {scan.get_string('id')}")
                #
                # scan.close()
                # tx3.commit()
                #
                # tx4 = db.new_transaction()
                # update_sql = "UPDATE test SET id = 'world' WHERE id = 'hello'"
                # print(f"Executing: {update_sql}")
                # planner.execute_update(update_sql, tx4)
                # tx4.commit()
                #
                # tx5 = db.new_transaction()
                # select_sql = "SELECT id FROM test"
                # print(f"Executing: {select_sql}")
                # plan = planner.create_query_plan(select_sql, tx5)
                # scan = plan.open()
                #
                # while scan.next():
                #     print(f"id = {scan.get_string('id')}")
                #
                # scan.close()
                # tx5.commit()
                #
                # tx6 = db.new_transaction()
                # delete_sql = "DELETE FROM test WHERE id = 'world'"
                # print(f"Executing: {delete_sql}")
                # planner.execute_update(delete_sql, tx6)
                # tx6.commit()
                #
                # tx5 = db.new_transaction()
                # select_sql = "SELECT id FROM test"
                # print(f"Executing33: {select_sql}")
                # plan = planner.create_query_plan(select_sql, tx5)
                # scan = plan.open()
                #
                # while scan.next():
                #     print(f"id = {scan.get_string('id')}")
                #
                # scan.close()
                # tx5.commit()

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
