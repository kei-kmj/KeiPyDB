import sys
from contextlib import contextmanager
from typing import Generator, List
from db.server.keipy_db import KeiPyDB
from db.constants import FieldType
from db.transaction.transaction import Transaction

# 定数定義
DEFAULT_DB_DIR: str = "data"
SQL_PROMPT: str = "SQL> "
EXIT_COMMAND: str = "exit"
SELECT_COMMAND: str = "select"
NULL_VALUE: str = "NULL"
GOODBYE_MESSAGE: str = "Goodbye!"
DATABASE_CONNECTED_MESSAGE: str = "Database connected"


class KeiPyClient:
    """KeiPyDB用のembedded SQLクライアント"""

    def __init__(self, db_dir: str = DEFAULT_DB_DIR) -> None:
        self.db: KeiPyDB = KeiPyDB(db_dir)
        self.planner = self.db.get_planner()
        print(DATABASE_CONNECTED_MESSAGE)

    @contextmanager
    def transaction(self) -> Generator[Transaction, None, None]:
        """トランザクション管理のコンテキストマネージャ"""
        tx: Transaction = self.db.new_transaction()
        try:
            yield tx
            tx.commit()
        except Exception as e:
            try:
                tx.rollback()
            except:
                pass
            raise e

    def run(self) -> None:
        """REPLループを実行する"""
        print(f"\n{SQL_PROMPT}", end="", flush=True)

        try:
            while True:
                try:
                    cmd: str = input().strip()

                    if cmd.lower().startswith(EXIT_COMMAND):
                        print(GOODBYE_MESSAGE)
                        break
                    elif cmd.lower().startswith(SELECT_COMMAND):
                        self._execute_select(cmd)
                    elif cmd:
                        self._execute_update(cmd)

                    print(f"\n{SQL_PROMPT}", end="", flush=True)

                except EOFError:
                    print(f"\n{GOODBYE_MESSAGE}")
                    break
                except KeyboardInterrupt:
                    print(f"\n{GOODBYE_MESSAGE}")
                    break

        except Exception as e:
            print(f"Client error: {e}")

    def _execute_select(self, cmd: str) -> None:
        """SELECT文を実行"""
        try:
            with self.transaction() as tx:
                plan = self.planner.create_query_plan(cmd, tx)
                scan = plan.open()

                # スキーマから利用可能なフィールドを取得
                schema = plan.schema()
                fields: List[str] = schema.get_fields()

                while scan.next():
                    field_values: List[str] = []
                    for field in fields:
                        try:
                            # フィールドの型に基づいて適切に取得
                            field_type: int = schema.get_type(field)
                            if field_type == FieldType.Integer:
                                value: int = scan.get_int(field)
                                field_values.append(f"{field} = {value}")
                            else:
                                value: str = scan.get_string(field)
                                field_values.append(f"{field} = {value}")
                        except Exception:
                            field_values.append(f"{field} = {NULL_VALUE}")

                    print(", ".join(field_values))

                scan.close()

        except Exception as e:
            print(f"SQL Exception: {e}")

    def _execute_update(self, cmd: str) -> None:
        """UPDATE系を実行"""
        try:
            with self.transaction() as tx:
                rows_affected: int = self.planner.execute_update(cmd, tx)
                print(f"{rows_affected} records processed")

        except Exception as e:
            print(f"SQL Exception: {e}")


def main() -> None:
    """メイン関数"""
    db_dir: str = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_DIR

    try:
        client: KeiPyClient = KeiPyClient(db_dir)
        client.run()
    except Exception as e:
        print(f"Failed to start client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()