class StatInfo:
    ESTIMATED_VALUE = 3

    def __init__(self, num_blocks: int, num_records: int) -> None:
        """統計情報オブジェクトを作成"""
        self.num_blocks = num_blocks
        self.num_records = num_records

    def estimate_blocks_quantity(self) -> int:
        """テーブル内の推定ブロック数"""
        return self.num_blocks

    def estimate_records_quantity(self) -> int:
        """テーブル内の推定レコード数"""
        return self.num_records

    def estimate_unique_values(self) -> int:
        """指定した列のユニークな値の数の推定値を返す"""
        return 1 + self.num_records // self.ESTIMATED_VALUE
