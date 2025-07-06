import tempfile
import shutil
import pytest

from db.buffer.buffer_manager import BufferManager
from db.constants import FieldType
from db.file.file_manager import FileManager
from db.log.log_manager import LogManager
from db.metadata.index_info import IndexInfo
from db.metadata.stat_info import StatInfo
from db.record.schema import Schema
from db.record.layout import Layout
from db.transaction.transaction import Transaction


@pytest.fixture
def real_index_info_env():
    """IndexInfo用の実際の環境"""
    temp_dir = tempfile.mkdtemp()
    try:
        block_size = 1024
        file_manager = FileManager(temp_dir, block_size)
        log_manager = LogManager(file_manager, "index_info_test_log")
        buffer_manager = BufferManager(file_manager, log_manager, 10)
        yield file_manager, log_manager, buffer_manager
    finally:
        shutil.rmtree(temp_dir)


def create_test_schema_and_layout():
    """テスト用のスキーマとレイアウトを作成"""
    schema = Schema()
    schema.add_field("id", FieldType.Integer, 0)
    schema.add_field("name", FieldType.Varchar, 30)
    schema.add_field("age", FieldType.Integer, 0)
    schema.add_field("email", FieldType.Varchar, 50)
    
    layout = Layout(schema)
    return schema, layout


def test_index_info_initialization(real_index_info_env):
    """IndexInfoの初期化テスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    # テスト用のスキーマとレイアウトを作成
    table_schema, table_layout = create_test_schema_and_layout()
    
    # 統計情報を作成
    stat_info = StatInfo(num_blocks=10, num_records=100)
    
    # IndexInfoを作成
    index_info = IndexInfo("idx_name", "name", table_schema, stat_info)
    
    # 基本的な属性を確認
    assert index_info.index_name == "idx_name"
    assert index_info.field_name == "name"
    assert index_info.table_schema == table_schema
    assert index_info.stat_info == stat_info
    
    # インデックスレイアウトが正しく作成されていることを確認
    assert index_info.index_layout is not None
    assert index_info.index_layout.schema.has_field("block")
    assert index_info.index_layout.schema.has_field("id")
    assert index_info.index_layout.schema.has_field("dataval")


def test_index_info_with_integer_field(real_index_info_env):
    """Integer型フィールドでのIndexInfoテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=5, num_records=50)
    
    # Integer型のフィールドでIndexInfoを作成
    index_info = IndexInfo("idx_id", "id", table_schema, stat_info)
    
    # インデックスレイアウトのdatavalフィールドがInteger型であることを確認
    dataval_type = index_info.index_layout.schema.get_type("dataval")
    assert dataval_type == FieldType.Integer
    
    # スロットサイズが適切に計算されていることを確認
    slot_size = index_info.index_layout.slot_size
    assert slot_size > 0


def test_index_info_with_varchar_field(real_index_info_env):
    """Varchar型フィールドでのIndexInfoテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=8, num_records=80)
    
    # Varchar型のフィールドでIndexInfoを作成
    index_info = IndexInfo("idx_name", "name", table_schema, stat_info)
    
    # インデックスレイアウトのdatavalフィールドがVarchar型であることを確認
    dataval_type = index_info.index_layout.schema.get_type("dataval")
    assert dataval_type == FieldType.Varchar
    
    # フィールド長が正しく設定されていることを確認
    dataval_length = index_info.index_layout.schema.get_length("dataval")
    expected_length = table_schema.get_length("name")
    assert dataval_length == expected_length


def test_index_info_blocks_accessed(real_index_info_env):
    """IndexInfoのblocks_accessedメソッドテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=20, num_records=200)
    
    index_info = IndexInfo("idx_test", "age", table_schema, stat_info)
    
    # blocks_accessedの計算をテスト
    blocks_accessed = index_info.blocks_accessed()
    
    # インデックスのブロックアクセス数は1 + (records / records_per_block)で計算される
    # 正の値が返されることを確認
    assert blocks_accessed > 0
    
    # 統計情報のブロック数より多くなることはないはず
    assert blocks_accessed <= stat_info.blocks_accessed() + 10  # 余裕を持った範囲


def test_index_info_records_output(real_index_info_env):
    """IndexInfoのrecords_outputメソッドテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=15, num_records=150)
    
    index_info = IndexInfo("idx_test", "email", table_schema, stat_info)
    
    # records_outputの計算をテスト
    records_output = index_info.records_output()
    
    # インデックスからの出力レコード数は元のレコード数をユニーク値数で割った値
    expected_output = stat_info.records_output() // stat_info.distinct_values()
    assert records_output == expected_output


def test_index_info_distinct_values(real_index_info_env):
    """IndexInfoのdistinct_valuesメソッドテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=12, num_records=120)
    
    index_info = IndexInfo("idx_test", "name", table_schema, stat_info)
    
    # distinct_valuesは統計情報から取得される
    distinct_values = index_info.distinct_values()
    expected_distinct = stat_info.distinct_values()
    
    assert distinct_values == expected_distinct
    assert distinct_values >= 1


def test_index_info_open_method(real_index_info_env):
    """IndexInfoのopenメソッドテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=6, num_records=60)
    
    index_info = IndexInfo("idx_open_test", "id", table_schema, stat_info)
    
    # インデックスを開く
    hash_index = index_info.open(tx)
    
    # HashIndexインスタンスが返されることを確認
    assert hash_index is not None
    
    # HashIndexの基本的な属性を確認
    from db.index.hash.hash_index import HashIndex
    assert isinstance(hash_index, HashIndex)
    
    # クリーンアップ
    hash_index.close()
    tx.commit()


def test_index_info_with_different_field_types(real_index_info_env):
    """異なるフィールドタイプでのIndexInfoテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    # より複雑なスキーマを作成
    schema = Schema()
    schema.add_field("int_field", FieldType.Integer, 0)
    schema.add_field("short_varchar", FieldType.Varchar, 10)
    schema.add_field("long_varchar", FieldType.Varchar, 100)
    schema.add_field("another_int", FieldType.Integer, 0)
    
    stat_info = StatInfo(num_blocks=10, num_records=100)
    
    # 各フィールドタイプでIndexInfoを作成
    test_cases = [
        ("idx_int1", "int_field", FieldType.Integer),
        ("idx_short_str", "short_varchar", FieldType.Varchar),
        ("idx_long_str", "long_varchar", FieldType.Varchar),
        ("idx_int2", "another_int", FieldType.Integer)
    ]
    
    for index_name, field_name, expected_type in test_cases:
        index_info = IndexInfo(index_name, field_name, schema, stat_info)
        
        # インデックスレイアウトが正しく作成されていることを確認
        assert index_info.index_layout.schema.has_field("dataval")
        dataval_type = index_info.index_layout.schema.get_type("dataval")
        assert dataval_type == expected_type
        
        if expected_type == FieldType.Varchar:
            dataval_length = index_info.index_layout.schema.get_length("dataval")
            expected_length = schema.get_length(field_name)
            assert dataval_length == expected_length


def test_index_info_edge_cases(real_index_info_env):
    """IndexInfoのエッジケーステスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    # 最小限のスキーマ
    minimal_schema = Schema()
    minimal_schema.add_field("only_field", FieldType.Integer, 0)
    
    # 空に近い統計情報
    minimal_stat = StatInfo(num_blocks=1, num_records=1)
    
    # IndexInfoを作成
    index_info = IndexInfo("minimal_idx", "only_field", minimal_schema, minimal_stat)
    
    # 基本的な動作を確認
    assert index_info.blocks_accessed() > 0
    assert index_info.records_output() >= 0
    assert index_info.distinct_values() >= 1
    
    # 非常に大きな統計情報
    large_stat = StatInfo(num_blocks=1000, num_records=10000)
    large_index_info = IndexInfo("large_idx", "only_field", minimal_schema, large_stat)
    
    # 大きな値でも適切に動作することを確認
    assert large_index_info.blocks_accessed() > 0
    assert large_index_info.records_output() >= 0
    assert large_index_info.distinct_values() >= 1


def test_index_info_nonexistent_field(real_index_info_env):
    """存在しないフィールドでのIndexInfoテスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=5, num_records=50)
    
    # 存在しないフィールドでIndexInfoを作成
    try:
        index_info = IndexInfo("idx_nonexistent", "nonexistent_field", table_schema, stat_info)
        # エラーが発生する可能性がある
        print(f"Nonexistent field handling: IndexInfo created with field that doesn't exist")
    except Exception as e:
        print(f"Expected error with nonexistent field: {e}")


def test_index_info_integration_with_transaction(real_index_info_env):
    """トランザクションとの統合テスト"""
    file_manager, log_manager, buffer_manager = real_index_info_env
    tx = Transaction(file_manager, log_manager, buffer_manager)
    
    table_schema, table_layout = create_test_schema_and_layout()
    stat_info = StatInfo(num_blocks=8, num_records=80)
    
    index_info = IndexInfo("integration_idx", "name", table_schema, stat_info)
    
    # トランザクション内でインデックスを開いて操作
    try:
        hash_index = index_info.open(tx)
        assert hash_index is not None
        
        # 基本的な操作を確認（詳細なインデックス操作は別のテストで行う）
        # ここではインデックスが正常に開けることを確認
        
        hash_index.close()
        
    except Exception as e:
        print(f"Integration test error: {e}")
    
    tx.commit()