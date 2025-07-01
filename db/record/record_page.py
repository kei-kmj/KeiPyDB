from typing import Optional

from db.constants import FieldType
from db.file.block_id import BlockID
from db.record.layout import Layout
from db.transaction.transaction import Transaction


class RecordPage:
    EMPTY = 0
    USED = 1

    def __init__(self, transaction: Transaction, block: BlockID, layout: Layout) -> None:
        self.transaction = transaction
        self.block = block
        self.layout = layout
        self.transaction.pin(block)

    def get_int(self, slot: int, field_name: str) -> int:
        """指定されたスロットの指定されたフィールドの整数値を返す"""
        field_position = self._offset(slot) + self.layout.get_offset(field_name)
        return self.transaction.get_int(self.block, field_position)

    def set_int(self, slot: int, field_name: str, value: int) -> None:
        """指定されたスロットの指定されたフィールドに整数値を設定する"""
        field_position = self._offset(slot) + self.layout.get_offset(field_name)
        self.transaction.set_int(self.block, field_position, value)

    def get_string(self, slot: int, field_name: str) -> str:
        """指定されたスロットの指定されたフィールドの文字列を返す"""
        field_position = self._offset(slot) + self.layout.get_offset(field_name)
        return self.transaction.get_string(self.block, field_position)

    def set_string(self, slot: int, field_name: str, value: str) -> None:
        """指定されたスロットの指定されたフィールドに文字列を設定する"""

        field_position = self._offset(slot) + self.layout.get_offset(field_name)
        self.transaction.set_string(self.block, field_position, value, ok_to_log=True)

    def delete(self, slot: int) -> None:
        """指定されたスロットを削除する"""
        self._set_flag(slot, RecordPage.EMPTY)

    def format(self) -> None:
        """このレコードページを初期化する"""
        slot = 0
        count = 0
        while self._is_valid_slot(slot):
            self.transaction.set_int(self.block, self._offset(slot), self.EMPTY, False)
            schema = self.layout.get_schema()
            for field_name in schema.get_fields():
                field_position = self._offset(slot) + self.layout.get_offset(field_name)
                if schema.get_type(field_name) == FieldType.Integer:
                    self.transaction.set_int(self.block, field_position, 0, False)
                else:
                    self.transaction.set_string(self.block, field_position, "", False)
            count += 1
            slot += 1

    def next_after(self, slot: int) -> int:
        """指定されたスロットの次の使用中のスロットを返す"""
        return self._search_after(slot, self.USED)

    def insert_after(self, slot: int) -> Optional[int]:
        """指定したスロットの次に空いているスロットを検索して使用中に設定"""
        new_slot = self._search_after(slot, self.EMPTY)
        if new_slot >= 0:
            self._set_flag(new_slot, self.USED)
        return new_slot

    def get_block(self) -> BlockID:
        """このレコードページのブロックを返す"""
        return self.block

    def _set_flag(self, slot: int, flag: int) -> None:
        """スロットの状態を設定する"""
        self.transaction.set_int(self.block, self._offset(slot), flag, True)

    def _search_after(self, slot: int, flag: int) -> int:
        """指定されたスロットの次に指定されたフラグを持つスロットを返す"""
        slot += 1
        while self._is_valid_slot(slot):
            if self.transaction.get_int(self.block, self._offset(slot)) == flag:
                return slot
            slot += 1

        return -1

    def _is_valid_slot(self, slot: int) -> bool:
        """指定されたスロットが有効かどうかを返す"""
        return slot >= 0 and self._offset(slot + 1) <= self.transaction.block_size()

    def _offset(self, slot: int) -> int:
        """指定されたスロットのオフセットを返す"""
        slot_size = self.layout.get_slot_size()
        offset = slot * slot_size
        return offset


