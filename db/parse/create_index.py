class CreateIndex:
    def __init__(self, index_name: str, table_name: str, field_name: str) -> None:
        self.index_name = index_name
        self.table_name = table_name
        self.field_name = field_name

    def get_index_name(self) -> str:
        """インデックス名を返す"""
        return self.index_name

    def get_table_name(self) -> str:
        """テーブル名を返す"""
        return self.table_name

    def get_field_name(self) -> str:
        """フィールド名を返す"""
        return self.field_name
