import sys
from db.server.keipy_db import KeiPyDB
from db.constants import FieldType


class KeiPyClient:
    """KeiPyDB用のembedded SQLクライアント"""

    def __init__(self, db_dir: str = "data"):
        self.db = KeiPyDB(db_dir)
        self.planner = self.db.get_planner()
        print("Database connected")

    def run(self) -> None:
        """REPLループを実行する"""
        print("\nSQL> ", end="", flush=True)

        try:
            while True:
                try:
                    cmd = input().strip()

                    if cmd.lower().startswith("exit"):
                        print("Goodbye!")
                        break
                    elif cmd.lower().startswith("select"):
                        self._execute_select(cmd)
                    elif cmd:
                        self._execute_update(cmd)

                    print("\nSQL> ", end="", flush=True)

                except EOFError:
                    print("\nGoodbye!")
                    break
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break

        except Exception as e:
            print(f"Client error: {e}")

    def _execute_select(self, cmd: str) -> None:
        """SELECT文を実行"""
        try:
            tx = self.db.new_transaction()
            plan = self.planner.create_query_plan(cmd, tx)
            scan = plan.open()

            # スキーマから利用可能なフィールドを取得
            schema = plan.schema()
            fields = schema.get_fields()

            while scan.next():
                # 各フィールドの値を取得して表示
                values = []
                for field in fields:
                    try:
                        # フィールドの型に基づいて適切に取得
                        field_type = schema.get_type(field)
                        if field_type == FieldType.Integer:
                            value = scan.get_int(field)
                            values.append(f"{field} = {value}")
                        else:  # FieldType.Varchar
                            value = scan.get_string(field)
                            values.append(f"{field} = {value}")
                    except Exception:
                        values.append(f"{field} = NULL")

                print(", ".join(values))

            scan.close()
            tx.commit()

        except Exception as e:
            print(f"SQL Exception: {e}")

    def _execute_update(self, cmd: str) -> None:
        """UPDATE系を実行"""
        try:
            tx = self.db.new_transaction()
            rows_affected = self.planner.execute_update(cmd, tx)
            tx.commit()
            print(f"{rows_affected} records processed")

        except Exception as e:
            print(f"SQL Exception: {e}")


def main():
    db_dir = sys.argv[1] if len(sys.argv) > 1 else "data"

    try:
        client = KeiPyClient(db_dir)
        client.run()
    except Exception as e:
        print(f"Failed to start client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()