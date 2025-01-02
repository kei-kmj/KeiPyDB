from db.constants import ByteSize, FieldType
from db.file.block_id import BlockID
from db.query.constant import Constant
from db.record.layout import Layout
from db.transaction.transaction import Transaction


class BtreePage:
    def __init__(self, transaction: Transaction, current_block: BlockID, layout: Layout):
        self.transaction = transaction
        self.current_block = current_block
        self.layout = layout
        self.transaction.pin(current_block)

    def find_slot_before(self, search_key: Constant) -> int:
        slot = 0

        while slot < self.get_num_records() and self.get_data_value(slot) < search_key:
            slot += 1

        return slot - 1

    def close(self) -> None:
        if self.current_block:
            self.transaction.unpin(self.current_block)

    def is_full(self) -> bool:
        return self.slot_position(self.get_num_records() + 1) >= self.transaction.block_size()

    def split(self, split_position: int, flag: int) -> BlockID:
        new_block = self.append_new(flag)
        new_page = BtreePage(self.transaction, new_block, self.layout)

        self.transfer_records(split_position, new_page)
        new_page.set_flag(flag)
        new_page.close()

        return new_block

    def get_num_records(self) -> int:
        return self.transaction.get_int(self.current_block, ByteSize.Int)

    def get_data_value(self, slot: int) -> Constant:
        return self.get_value(slot, "data_value")

    def get_value(self, slot: int, field_name: str) -> Constant:
        schema_type = self.layout.get_schema().get_type(field_name)
        if schema_type == FieldType.Integer:
            return Constant(self.get_int(slot, field_name))

        else:
            return Constant(self.get_string(slot, field_name))

    def get_int(self, slot: int, field_name: str) -> int:
        position = self.get_field_position(slot, field_name)
        return self.transaction.get_int(self.current_block, position)

    def set_int(self, slot: int, field_name: str, value: int) -> None:
        position = self.get_field_position(slot, field_name)
        self.transaction.set_int(self.current_block, position, value, True)

    def get_string(self, slot: int, field_name: str) -> str:
        position = self.get_field_position(slot, field_name)
        return self.transaction.get_string(self.current_block, position)

    def set_string(self, slot: int, field_name: str, value: str) -> None:
        position = self.get_field_position(slot, field_name)
        self.transaction.set_string(self.current_block, position, value, True)

    def get_flag(self) -> int:
        return self.transaction.get_int(self.current_block, 0)

    def set_flag(self, value: int) -> None:
        self.transaction.set_int(self.current_block, 0, value, True)

    def get_field_position(self, slot: int, field_name: str) -> int:
        offset = self.layout.get_offset(field_name)
        return self.slot_position(slot) + offset

    def slot_position(self, slot: int) -> int:
        slot_size = self.layout.get_slot_size()
        slot_header_size = ByteSize.Int * 2
        return slot_header_size + slot * slot_size

    def transfer_records(self, slot: int, dest_page: "BtreePage") -> None:
        dest_slot = 0

        while slot < self.get_num_records():
            dest_page.insert(dest_slot)
            schema = self.layout.get_schema()

            for field_name in schema.get_fields():
                dest_page.set_value(dest_slot, field_name, self.get_value(slot, field_name))

            self.delete(slot)
            dest_slot += 1

    def insert(self, slot: int) -> None:
        for i in range(self.get_num_records(), slot, -1):
            self.copy_record(i - 1, i)

        self.set_num_records(self.get_num_records() + 1)

    def set_value(self, slot: int, field_name: str, value: Constant) -> None:
        field_type = self.layout.schema.get_type(field_name)

        if field_type == FieldType.Integer:
            self.set_int(slot, field_name, value.as_int())
        else:
            self.set_string(slot, field_name, value.as_string())

    def copy_record(self, from_slot: int, to_slot: int) -> None:
        schema = self.layout.get_schema()

        for field_name in schema.get_fields():
            self.set_value(to_slot, field_name, self.get_value(from_slot, field_name))

    def set_num_records(self, n: int) -> None:
        self.transaction.set_int(self.current_block, ByteSize.Int, n, True)

    def delete(self, slot: int) -> None:
        for i in range(slot + 1, self.get_num_records()):
            self.copy_record(i, i - 1)

        self.set_num_records(self.get_num_records() - 1)

    def append_new(self, flag: int) -> BlockID:
        block = self.transaction.append(self.current_block.file_name)
        self.transaction.pin(block)
        self.format(block, flag)

        return block

    def format(self, block: BlockID, flag: int) -> None:
        self.transaction.set_int(block, 0, flag, False)
        self.transaction.set_int(block, ByteSize.Int, 0, False)
        record_size = self.layout.get_slot_size()

        for position in range(ByteSize.Int * 2, self.transaction.block_size(), record_size):
            self.make_default_record(block, position)

    def make_default_record(self, block: BlockID, position: int) -> None:
        for field_name in self.layout.schema.get_fields():
            offset = self.layout.get_offset(field_name)

            if self.layout.schema.get_type(field_name) == FieldType.Integer:
                self.transaction.set_int(block, position + offset, 0, False)
            else:
                self.transaction.set_string(block, position + offset, "", False)


    def get_child_number(self, slot: int) -> int:
        return self.get_int(slot, "block")

    def insert_directory(self, slot: int, value: Constant, block_number: int) -> None:
        self.insert(slot)
        self.set_value(slot, "data_value", value)
        self.set_int(slot, "block", block_number)
