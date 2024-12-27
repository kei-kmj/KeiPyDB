class RecordID:
    def __init__(self, block_number: int, slot: int) -> None:
        self.block_number = block_number
        self.slot = slot

    def __eq__(self, target_record: object) -> bool:
        if not isinstance(target_record, RecordID):
            return False

        return self.block_number == target_record.block_number and self.slot == target_record.slot

    def __repr__(self) -> str:
        """RecordIDを文字列に変換"""
        return f"[block {self.block_number}, slot {self.slot}]"

    def get_block_number(self) -> int:
        """ブロック番号を返す"""
        return self.block_number

    def get_slot(self) -> int:
        """スロット番号を返す"""
        return self.slot
