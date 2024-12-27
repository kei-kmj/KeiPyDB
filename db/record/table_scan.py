from db.constants import FieldType
from db.file.block_id import BlockID
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.record.record_page import RecordPage
from db.transaction.transaction import Transaction


class TableScan:
    def __init__(self, transaction: Transaction, table_name: str, layout: Layout) -> None:
        self.transaction = transaction
        self.layout = layout
        self.file_name = f"{table_name}.tbl"
        self.current_slot = -1
        self.record_page = None

        try:
            if self.transaction.size(self.file_name) == 0:
                self._move_to_new_block()

            else:
                self._move_to_block(0)
        except FileNotFoundError:
            raise FileNotFoundError(f"Table {table_name} does not exist")

    def buffer_first(self) -> None:
        """最初のブロックをバッファに読み込む"""
        self._move_to_block(0)


    def next(self) -> bool:
        """次のレコードに移動する"""
        self.current_slot = self.record_page.next_after(self.current_slot)
        while self.current_slot < 0:
            if self._at_last_block():
                return False
            self._move_to_block(self.record_page.get_block().number + 1)
            self.current_slot = self.record_page.next_after(self.current_slot)

        return True

    def get_int(self, field_name: str) -> int:
        """現在のスロットの指定されたフィールドの整数値を返す"""
        return self.record_page.get_int(self.current_slot, field_name)


    def get_string(self, field_name: str) -> str:
        """現在のスロットの指定されたフィールドの文字列を返す"""
        return self.record_page.get_string(self.current_slot, field_name)


    def get_val(self, field_name: str) -> int | str:
        """現在のスロットの指定されたフィールドの値を返す"""
        field_type = self.layout.get_schema().get_type(field_name)
        if field_type == FieldType.Integer:
            return self.get_int(field_name)
        elif field_type == FieldType.Varchar:
            return self.get_string(field_name)
        else:
            raise ValueError(f"Unknown field type {field_type}")

    def has_field(self, field_name: str) -> bool:
        """指定されたフィールドが含まれているかどうかを返す"""
        return self.layout.schema.has_field(field_name)


    def close(self) -> None:
        """スキャンを閉じる"""
        if self.record_page is not None:
            self.transaction.unpin(self.record_page.get_block())


    def set_int(self, field_name: str, value: int) -> None:
        """現在のスロットの指定されたフィールドに整数値を設定する"""
        self.record_page.set_int(self.current_slot, field_name, value)


    def set_string(self, field_name: str, value: str) -> None:
        """現在のスロットの指定されたフィールドに文字列を設定する"""
        self.record_page.set_string(self.current_slot, field_name, value)

    def set_val(self, field_name: str, value) -> None:
        """現在のスロットの指定されたフィールドに値を設定"""
        if self.layout.get_schema().get_type(field_name) == FieldType.Integer:
            self.set_int(field_name, int(value))
        else:
            self.set_string(field_name, str(value))


    def insert(self) -> None:
        """新しいスロットを挿入する"""
        while True:
            self.current_slot = self.record_page.insert_after(self.current_slot)
            if self.current_slot >= 0:
                break
            if self._at_last_block():
                self._move_to_new_block()
            else:
                self._move_to_block(self.record_page.get_block().number + 1)

    def delete(self) -> None:
        """現在のスロットを削除する"""
        self.record_page.delete(self.current_slot)

    def move_to_rid(self, rid: RecordID) -> None:
        """指定されたRIDに移動する"""
        if rid.block_number != self.record_page.get_block().number:
            self._move_to_block(rid.block_number)
        self.current_slot = rid.slot

    def get_rid(self) -> RecordID:
        """現在のRIDを返す"""
        return RecordID(self.record_page.get_block().number, self.current_slot)

    def _move_to_block(self, block_number: int) -> None:
        """指定されたブロックに移動する"""
        self.close()
        block = BlockID(self.file_name, block_number)
        self.record_page = RecordPage(self.transaction, block, self.layout)
        self.current_slot = -1

    def _move_to_new_block(self) -> None:
        """新しいブロックを作成して移動する"""
        self.close()
        block = self.transaction.append(self.file_name)
        self.record_page = RecordPage(self.transaction, block, self.layout)
        self.record_page.format()
        self.current_slot = -1

    def _at_last_block(self) -> bool:
        """最後のブロックにいるかどうかを返す"""
        return self.record_page.get_block().number == self.transaction.size(self.file_name) - 1