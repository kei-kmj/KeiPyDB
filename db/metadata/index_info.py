from db.constants import FieldType
from db.index.hash.hash_index import HashIndex
from db.index.index import Index
from db.metadata.stat_info import StatInfo
from db.record.layout import Layout
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class IndexInfo:
    def __init__(
        self, index_name: str, field_name: str, table_schema: Schema, transaction: Transaction, stat_info: StatInfo
    ) -> None:
        self.index_name = index_name
        self.field_name = field_name
        self.table_schema = table_schema
        self.transaction = transaction
        self.index_layout = self._create_index_layout()
        self.stat_info = stat_info

    # TODO:HshIndexクラスを実装
    def open(self) -> Index:
        """インデックスを開く"""
        return HashIndex(self.transaction, self.index_name, self.index_layout)

    def blocks_accessed(self) -> int:
        """アクセスしたブロック数を返す"""
        return self.stat_info.records_output() // self.stat_info.distinct_values()

    # TODO:distinct_values()の引数確認
    def records_output(self) -> int:
        """出力されたレコード数を返す"""
        return self.stat_info.records_output() // self.stat_info.distinct_values()

    def distinct_values(self, field_name: str) -> int:
        return 1 if field_name == self.field_name else self.stat_info.distinct_values()

    def _create_index_layout(self) -> Layout:
        """インデックスのレイアウトを作成"""
        schema = Schema()
        schema.add_int_field("block")
        schema.add_int_field("id")

        if self.table_schema.get_type(self.field_name) == FieldType.Integer:
            schema.add_string_field("dat", self.table_schema.get_length(self.field_name))

        else:
            field_length = self.table_schema.get_length(self.field_name)
            schema.add_string_field("dat", field_length)

        return Layout(schema)
