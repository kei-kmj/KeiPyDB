"""
基本的なSQL操作（SELECT、INSERT、CREATE TABLE、DELETE）の成功を確認するテスト
プロダクションコード修正時の回帰テストとして使用
"""

import pytest
import tempfile
import shutil
import os

from db.server.keipy_db import KeiPyDB


class TestBasicSQLOperations:
    """基本的なSQL操作が成功することを確認するテスト"""
    
    @pytest.fixture
    def fresh_db(self):
        """新しいデータベース環境を作成"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # クリーンアップ
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_create_table_success(self, fresh_db):
        """CREATE TABLEが成功することを確認"""
        db = KeiPyDB(fresh_db)
        planner = db.get_planner()
        tx = db.new_transaction()
        
        # テーブル作成
        create_sql = "CREATE TABLE test_table (id varchar(10), name varchar(50), age varchar(10))"
        result = planner.execute_update(create_sql, tx)
        tx.commit()
        
        # 成功を確認（エラーが発生しないこと）
        assert result == 0  # CREATE TABLEは通常0を返す
        print("✓ CREATE TABLE成功")
    
    def test_insert_success(self, fresh_db):
        """INSERTが成功することを確認"""
        db = KeiPyDB(fresh_db)
        planner = db.get_planner()
        
        # テーブル作成
        tx1 = db.new_transaction()
        create_sql = "CREATE TABLE users (id varchar(10), name varchar(50))"
        planner.execute_update(create_sql, tx1)
        tx1.commit()
        
        # データ挿入
        tx2 = db.new_transaction()
        insert_sql = "INSERT INTO users (id, name) VALUES ('1', 'Alice')"
        result = planner.execute_update(insert_sql, tx2)
        tx2.commit()
        
        # 成功を確認
        assert result == 1  # INSERTは通常1を返す（1行挿入）
        print("✓ INSERT成功")
    
    def test_select_success(self, fresh_db):
        """SELECTが成功することを確認"""
        db = KeiPyDB(fresh_db)
        planner = db.get_planner()
        
        # テーブル作成とデータ挿入
        tx1 = db.new_transaction()
        planner.execute_update("CREATE TABLE products (id varchar(10), name varchar(50))", tx1)
        tx1.commit()
        
        tx2 = db.new_transaction()
        planner.execute_update("INSERT INTO products (id, name) VALUES ('1', 'Laptop')", tx2)
        planner.execute_update("INSERT INTO products (id, name) VALUES ('2', 'Mouse')", tx2)
        tx2.commit()
        
        # データ取得
        tx3 = db.new_transaction()
        select_sql = "SELECT id, name FROM products"
        plan = planner.create_query_plan(select_sql, tx3)
        scan = plan.open()
        
        # 結果を収集
        results = []
        scan.before_first()
        while scan.next():
            record = {
                'id': scan.get_string('id'),
                'name': scan.get_string('name')
            }
            results.append(record)
        
        scan.close()
        tx3.commit()
        
        # 成功を確認
        assert len(results) == 2
        print(f"✓ SELECT成功: {len(results)}件取得")
        for r in results:
            print(f"  - id: {r['id']}, name: {r['name']}")
    
    def test_delete_success(self, fresh_db):
        """DELETEが成功することを確認"""
        db = KeiPyDB(fresh_db)
        planner = db.get_planner()
        
        # テーブル作成とデータ挿入
        tx1 = db.new_transaction()
        planner.execute_update("CREATE TABLE items (id varchar(10), status varchar(20))", tx1)
        tx1.commit()
        
        tx2 = db.new_transaction()
        planner.execute_update("INSERT INTO items (id, status) VALUES ('1', 'active')", tx2)
        planner.execute_update("INSERT INTO items (id, status) VALUES ('2', 'inactive')", tx2)
        planner.execute_update("INSERT INTO items (id, status) VALUES ('3', 'active')", tx2)
        tx2.commit()
        
        # データ削除
        tx3 = db.new_transaction()
        delete_sql = "DELETE FROM items WHERE status = 'inactive'"
        result = planner.execute_update(delete_sql, tx3)
        tx3.commit()
        
        # 削除後の確認
        tx4 = db.new_transaction()
        plan = planner.create_query_plan("SELECT id FROM items", tx4)
        scan = plan.open()
        
        remaining_count = 0
        scan.before_first()
        while scan.next():
            remaining_count += 1
        
        scan.close()
        tx4.commit()
        
        # 成功を確認
        assert result >= 1  # 少なくとも1行削除
        assert remaining_count == 2  # 2行残っている
        print(f"✓ DELETE成功: {result}件削除、{remaining_count}件残存")
    
    def test_full_crud_scenario(self, fresh_db):
        """完全なCRUDシナリオが成功することを確認"""
        db = KeiPyDB(fresh_db)
        planner = db.get_planner()
        
        print("\n=== 完全なCRUDシナリオテスト ===")
        
        # 1. CREATE TABLE
        tx1 = db.new_transaction()
        create_result = planner.execute_update(
            "CREATE TABLE employees (id varchar(10), name varchar(50), department varchar(30))", 
            tx1
        )
        tx1.commit()
        assert create_result == 0
        print("✓ 1. CREATE TABLE成功")
        
        # 2. INSERT（複数行）
        tx2 = db.new_transaction()
        insert_data = [
            ("1", "Alice", "Engineering"),
            ("2", "Bob", "Sales"),
            ("3", "Charlie", "Engineering"),
            ("4", "Diana", "HR")
        ]
        
        for id_val, name, dept in insert_data:
            sql = f"INSERT INTO employees (id, name, department) VALUES ('{id_val}', '{name}', '{dept}')"
            result = planner.execute_update(sql, tx2)
            assert result == 1
        tx2.commit()
        print(f"✓ 2. INSERT成功: {len(insert_data)}件挿入")
        
        # 3. SELECT（条件付き）
        tx3 = db.new_transaction()
        plan = planner.create_query_plan("SELECT name FROM employees WHERE department = 'Engineering'", tx3)
        scan = plan.open()
        
        eng_employees = []
        scan.before_first()
        while scan.next():
            eng_employees.append(scan.get_string('name'))
        
        scan.close()
        tx3.commit()
        
        assert len(eng_employees) == 2
        print(f"✓ 3. SELECT成功: Engineering部門 {len(eng_employees)}名")
        
        # 4. UPDATE
        tx4 = db.new_transaction()
        update_result = planner.execute_update(
            "UPDATE employees SET department = 'Marketing' WHERE name = 'Bob'",
            tx4
        )
        tx4.commit()
        assert update_result >= 1
        print(f"✓ 4. UPDATE成功: {update_result}件更新")
        
        # 5. DELETE
        tx5 = db.new_transaction()
        delete_result = planner.execute_update(
            "DELETE FROM employees WHERE department = 'HR'",
            tx5
        )
        tx5.commit()
        assert delete_result >= 1
        print(f"✓ 5. DELETE成功: {delete_result}件削除")
        
        # 6. 最終確認
        tx6 = db.new_transaction()
        plan = planner.create_query_plan("SELECT id, name, department FROM employees", tx6)
        scan = plan.open()
        
        final_employees = []
        scan.before_first()
        while scan.next():
            emp = {
                'id': scan.get_string('id'),
                'name': scan.get_string('name'),
                'department': scan.get_string('department')
            }
            final_employees.append(emp)
        
        scan.close()
        tx6.commit()
        
        assert len(final_employees) == 3  # 4人から1人削除で3人
        print(f"✓ 6. 最終確認: {len(final_employees)}名の従業員")
        for emp in final_employees:
            print(f"     - {emp['name']} ({emp['department']})")
        
        print("\n✅ 完全なCRUDシナリオ成功！")


def run_basic_sql_tests():
    """スタンドアロンでテストを実行"""
    import sys
    
    print("=== 基本SQL操作テスト開始 ===\n")
    
    test_instance = TestBasicSQLOperations()
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 各テストを実行
        tests = [
            ("CREATE TABLE", test_instance.test_create_table_success),
            ("INSERT", test_instance.test_insert_success),
            ("SELECT", test_instance.test_select_success),
            ("DELETE", test_instance.test_delete_success),
            ("完全なCRUD", test_instance.test_full_crud_scenario)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name}テスト ---")
            try:
                # 各テスト用の新しいディレクトリ
                test_dir = tempfile.mkdtemp()
                test_func(test_dir)
                passed += 1
                print(f"✅ {test_name}テスト: PASSED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name}テスト: FAILED")
                print(f"   エラー: {e}")
            finally:
                if os.path.exists(test_dir):
                    shutil.rmtree(test_dir)
        
        print(f"\n\n=== テスト結果 ===")
        print(f"成功: {passed}")
        print(f"失敗: {failed}")
        print(f"合計: {passed + failed}")
        
        if failed == 0:
            print("\n🎉 すべてのテストが成功しました！")
            print("基本的なSQL操作は正常に動作しています。")
        else:
            print("\n⚠️  一部のテストが失敗しました。")
            sys.exit(1)
            
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    run_basic_sql_tests()