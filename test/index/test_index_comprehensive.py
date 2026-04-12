import shutil
import tempfile

import pytest

from db.buffer.buffer_manager import BufferManager
from db.constants import FieldType
from db.file.file_manager import FileManager
from db.index.hash.hash_index import HashIndex
from db.log.log_manager import LogManager
from db.metadata.metadata_manager import MetadataManager
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


@pytest.fixture
def real_db_env():
    """インデックステスト用の実際のDB環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 10)

        transaction = Transaction(file_manager, log_manager, buffer_manager)
        metadata_manager = MetadataManager(True, transaction)
        transaction.commit()

        fresh_transaction = Transaction(file_manager, log_manager, buffer_manager)
        yield file_manager, log_manager, buffer_manager, metadata_manager, fresh_transaction
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_table_with_data(real_db_env):
    """サンプルデータ付きのテストテーブルを作成"""
    file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

    schema = Schema()
    schema.add_field("id", FieldType.Integer, 0)
    schema.add_field("name", FieldType.Varchar, 50)
    schema.add_field("age", FieldType.Integer, 0)

    metadata_manager.create_table("test_table", schema, transaction)
    layout = metadata_manager.get_layout("test_table", transaction)

    table_scan = TableScan(transaction, "test_table", layout)
    test_data = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
        {"id": 3, "name": "Charlie", "age": 22},
        {"id": 4, "name": "Diana", "age": 28},
        {"id": 5, "name": "Eve", "age": 35},
    ]

    record_ids = []
    for data in test_data:
        table_scan.insert()
        table_scan.set_int("id", data["id"])
        table_scan.set_string("name", data["name"])
        table_scan.set_int("age", data["age"])
        record_ids.append(table_scan.get_rid())

    table_scan.close()
    transaction.commit()

    fresh_transaction = Transaction(file_manager, log_manager, buffer_manager)
    yield metadata_manager, fresh_transaction, "test_table", schema, layout, test_data, record_ids


def _create_int_index_layout() -> Layout:
    """整数型のインデックスレイアウトを作成"""
    schema = Schema()
    schema.add_field("block", FieldType.Integer, 0)
    schema.add_field("id", FieldType.Integer, 0)
    schema.add_field("data_value", FieldType.Integer, 0)
    return Layout(schema)


class TestHashIndex:
    """HashIndexの基本動作テスト"""

    def test_hash_index_creation_and_basic_operations(self, test_table_with_data):
        """HashIndexの作成と基本操作のテスト"""
        metadata_manager, transaction, table_name, schema, layout, test_data, record_ids = test_table_with_data

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "test_id_index", index_layout)

        for i, record_id in enumerate(record_ids):
            data_value = Constant(test_data[i]["id"])
            hash_index.before_first(data_value)
            hash_index.insert(data_value, record_id)

        search_key = Constant(3)
        hash_index.before_first(search_key)
        found_records = []
        while hash_index.next():
            found_records.append(hash_index.get_data_record_id())

        assert len(found_records) > 0

        search_key_missing = Constant(999)
        hash_index.before_first(search_key_missing)
        missing_records = []
        while hash_index.next():
            missing_records.append(hash_index.get_data_record_id())

        assert len(missing_records) == 0

        hash_index.close()

    def test_hash_index_bucket_distribution(self, real_db_env):
        """バケット分散のテスト"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "distribution_test", index_layout)

        test_values = [1, 2, 3, 100, 101, 200, 201]
        for value in test_values:
            record_id = RecordID(0, value)
            hash_index.before_first(Constant(value))
            hash_index.insert(Constant(value), record_id)

        found_count = 0
        for value in test_values:
            hash_index.before_first(Constant(value))
            if hash_index.next():
                found_count += 1

        assert found_count == len(test_values)
        hash_index.close()

    def test_hash_index_deletion(self, real_db_env):
        """削除操作のテスト"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "deletion_test", index_layout)

        test_records = [
            (Constant(10), RecordID(1, 1)),
            (Constant(20), RecordID(1, 2)),
            (Constant(30), RecordID(1, 3)),
        ]

        for data_value, record_id in test_records:
            hash_index.before_first(data_value)
            hash_index.insert(data_value, record_id)

        data_value_to_delete = Constant(20)
        record_id_to_delete = RecordID(1, 2)
        hash_index.before_first(data_value_to_delete)
        hash_index.delete(data_value_to_delete, record_id_to_delete)

        hash_index.before_first(data_value_to_delete)
        assert not hash_index.next()

        for data_value, _ in [(Constant(10), None), (Constant(30), None)]:
            hash_index.before_first(data_value)
            assert hash_index.next()

        hash_index.close()

    def test_hash_index_delete_nonexistent_raises(self, real_db_env):
        """存在しないレコードの削除でValueErrorが発生することを確認"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "delete_nonexistent_test", index_layout)

        hash_index.before_first(Constant(999))
        with pytest.raises(ValueError):
            hash_index.delete(Constant(999), RecordID(999, 999))

        hash_index.close()

    def test_hash_index_search_cost_calculation(self):
        """search_costの計算テスト"""
        test_cases = [
            (100, 10, 1),
            (1000, 10, 1),
            (50, 10, 1),
        ]
        for num_blocks, records_per_block, min_expected in test_cases:
            actual_cost = HashIndex.search_cost(num_blocks, records_per_block)
            assert actual_cost >= min_expected


class TestIndexIntegration:
    """インデックスと他コンポーネントの統合テスト"""

    def test_index_transaction_isolation(self, real_db_env):
        """トランザクション分離のテスト"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction1 = real_db_env
        transaction2 = Transaction(file_manager, log_manager, buffer_manager)

        index_layout = _create_int_index_layout()
        hash_index1 = HashIndex(transaction1, "isolation_test1", index_layout)
        hash_index2 = HashIndex(transaction2, "isolation_test2", index_layout)

        hash_index1.before_first(Constant(100))
        hash_index1.insert(Constant(100), RecordID(1, 1))

        hash_index2.before_first(Constant(200))
        hash_index2.insert(Constant(200), RecordID(2, 1))

        hash_index1.before_first(Constant(100))
        assert hash_index1.next()

        hash_index2.before_first(Constant(200))
        assert hash_index2.next()

        hash_index1.close()
        hash_index2.close()
        transaction2.commit()

    def test_index_with_table_integration(self, test_table_with_data):
        """テーブルデータとの統合テスト"""
        metadata_manager, transaction, table_name, schema, layout, test_data, record_ids = test_table_with_data

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "table_integration_test", index_layout)

        for i, record_id in enumerate(record_ids):
            id_value = test_data[i]["id"]
            hash_index.before_first(Constant(id_value))
            hash_index.insert(Constant(id_value), record_id)

        target_id = 3
        hash_index.before_first(Constant(target_id))

        found_records = []
        while hash_index.next():
            index_record_id = hash_index.get_data_record_id()
            table_scan = TableScan(transaction, table_name, layout)
            table_scan.move_to_rid(index_record_id)
            found_records.append(
                {
                    "id": table_scan.get_int("id"),
                    "name": table_scan.get_string("name"),
                }
            )
            table_scan.close()

        assert len(found_records) > 0
        assert found_records[0]["id"] == target_id

        hash_index.close()


class TestIndexErrorConditions:
    """インデックスのエラー条件テスト"""

    def test_next_without_before_first_raises(self, real_db_env):
        """before_first未呼び出しでnext()がRuntimeErrorを発生させることを確認"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "uninitialized_test", index_layout)

        with pytest.raises(RuntimeError):
            hash_index.next()

        hash_index.close()

    def test_get_data_record_id_without_before_first_raises(self, real_db_env):
        """before_first未呼び出しでget_data_record_id()がRuntimeErrorを発生させることを確認"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "uninitialized_rid_test", index_layout)

        with pytest.raises(RuntimeError):
            hash_index.get_data_record_id()

        hash_index.close()

    def test_duplicate_keys_allowed(self, real_db_env):
        """重複キーの挿入が許可されることを確認"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "duplicate_test", index_layout)

        hash_index.before_first(Constant(1))
        hash_index.insert(Constant(1), RecordID(1, 1))
        hash_index.insert(Constant(1), RecordID(2, 2))

        hash_index.before_first(Constant(1))
        found_count = 0
        while hash_index.next():
            found_count += 1
            if found_count > 10:
                break

        assert found_count == 2
        hash_index.close()

    def test_boundary_values(self, real_db_env):
        """境界値のテスト"""
        file_manager, log_manager, buffer_manager, metadata_manager, transaction = real_db_env

        index_layout = _create_int_index_layout()
        hash_index = HashIndex(transaction, "boundary_test", index_layout)

        extreme_values = [Constant(-999999), Constant(0), Constant(999999)]
        for i, extreme_value in enumerate(extreme_values):
            hash_index.insert(extreme_value, RecordID(0, i))
            hash_index.before_first(extreme_value)
            assert hash_index.next()

        hash_index.close()
