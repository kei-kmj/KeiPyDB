class StatInfo:
    ESTIMATED_VALUE = 3

    def __init__(self, num_blocks: int, num_records: int) -> None:
        """統計情報オブジェクトを作成"""
        self.num_blocks = num_blocks
        self.num_records = num_records

    def blocks_accessed(self) -> int:
        """ブロックアクセス数を返す"""
        return self.num_blocks

    def records_output(self) -> int:
        """出力レコード数を返す"""
        return self.num_records

    def distinct_values(self) -> int:
        """フィールドの値の種類数を返す"""
        return 1 + (self.num_records // StatInfo.ESTIMATED_VALUE)
