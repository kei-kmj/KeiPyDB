from db.constants import FieldType
from db.index.hash.hash_index import HashIndex
from db.index.index import Index
from db.metadata.stat_info import StatInfo
from db.record.layout import Layout
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class IndexInfo:
    def __init__(self, index_name: str, field_name: str, table_schema: Schema, stat_info: StatInfo) -> None:
        self.index_name = index_name
        self.field_name = field_name
        self.table_schema = table_schema
        self.index_layout = self._create_index_layout()
        self.stat_info = stat_info

    def open(self, transaction: Transaction) -> Index:
        """インデックスを開く"""
        return HashIndex(transaction, self.index_name, self.index_layout)

    def blocks_accessed(self, transaction: Transaction) -> int:
        """アクセスしたブロック数を返す"""
        record_per_block = transaction.block_size() // self.index_layout.slot_size
        num_blocks = self.stat_info.records_output() // record_per_block
        return HashIndex.search_cost(num_blocks, record_per_block)

    def records_output(self) -> int:
        """出力されたレコード数を返す"""
        return self.stat_info.records_output() // self.stat_info.distinct_values()

    def distinct_values(self) -> int:
        return self.stat_info.distinct_values()

    def _create_index_layout(self) -> Layout:
        """インデックスのレイアウトを作成"""
        schema = Schema()
        schema.add_int_field("block")
        schema.add_int_field("id")

        if self.table_schema.get_type(self.field_name) == FieldType.Integer:
            schema.add_int_field("dataval")
        else:
            field_length = self.table_schema.get_length(self.field_name)
            schema.add_string_field("dataval", field_length)

        return Layout(schema)
