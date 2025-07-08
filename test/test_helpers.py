"""
Database testing helper functions
テスト用のヘルパー関数
"""

import os
import shutil
import tempfile

import pytest
from db.server.keipy_db import KeiPyDB


def create_fresh_db_directory():
    """
    新しい一時ディレクトリを作成してデータベース用に使用
    Returns: (temp_dir_path, cleanup_function)
    """
    temp_dir = tempfile.mkdtemp(prefix="keipy_test_")

    def cleanup():
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return temp_dir, cleanup


def cleanup_test_directory(dir_path):
    """
    テストディレクトリを削除
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        print(f"Cleaned up test directory: {dir_path}")


# Removed test_with_fresh_db - This is a decorator, not a test


def create_test_database(dir_path):
    """
    テスト用のデータベースを作成
    Returns: KeiPyDB instance
    """
    return KeiPyDB(dir_path)


def run_sql_commands(db, commands):
    """
    一連のSQLコマンドを実行
    Args:
        db: KeiPyDB instance
        commands: list of SQL command strings
    Returns: list of results
    """
    planner = db.get_planner()
    results = []

    for command in commands:
        tx = db.new_transaction()
        try:
            if command.strip().upper().startswith("SELECT"):
                # Query command
                plan = planner.create_query_plan(command, tx)
                scan = plan.open()

                query_results = []
                scan.before_first()
                while scan.next():
                    # 簡単な例：最初のフィールドのみ取得
                    # より複雑な結果取得が必要な場合は拡張
                    try:
                        # フィールド名を推測（改善の余地あり）
                        if "id" in command.lower():
                            value = scan.get_string("id")
                            query_results.append({"id": value})
                    except:
                        pass

                scan.close()
                results.append({"command": command, "type": "query", "results": query_results})
            else:
                # Update command (CREATE, INSERT, UPDATE, DELETE)
                result = planner.execute_update(command, tx)
                results.append({"command": command, "type": "update", "result": result})

            tx.commit()
        except Exception as e:
            try:
                tx.rollback()
            except:
                pass
            results.append({"command": command, "type": "error", "error": str(e)})

    return results


# 使用例とテスト
if __name__ == "__main__":

    @test_with_fresh_db
    def sample_test(db_dir):
        print(f"Testing with fresh database in: {db_dir}")

        # データベース作成
        db = create_test_database(db_dir)

        # テストコマンド実行
        commands = [
            "CREATE TABLE sample (id varchar(10), name varchar(20))",
            "INSERT INTO sample (id, name) VALUES ('1', 'test')",
            "SELECT id FROM sample",
        ]

        results = run_sql_commands(db, commands)

        for result in results:
            print(f"Command: {result['command']}")
            print(f"Type: {result['type']}")
            if result["type"] == "query":
                print(f"Results: {result['results']}")
            elif result["type"] == "update":
                print(f"Update result: {result['result']}")
            elif result["type"] == "error":
                print(f"Error: {result['error']}")
            print("---")

    # テスト実行
    sample_test()
