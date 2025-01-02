from db.constants import NODE_DIVISOR, Node, Slot
from db.file.block_id import BlockID
from db.index.btree.btree_page import BtreePage
from db.index.btree.dir_entry import DirectoryEntry
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.transaction.transaction import Transaction


class BtreeLeaf:

    def __init__(self, transaction: Transaction, block: BlockID, layout: Layout, search_key: Constant) -> None:
        self.transaction = transaction
        self.block = block
        self.layout = layout
        self.search_key = search_key
        self.contents = BtreePage(transaction, block, layout)
        self.current_slot = self.contents.find_slot_before(search_key)
        self.file_name = block.file_name

    def close(self) -> None:
        self.contents.close()

    def next(self) -> bool:
        self.current_slot += 1

        if self.current_slot >= self.contents.get_num_records():
            return self.try_over_flow()

        elif self.contents.get_data_value(self.current_slot) == self.search_key:
            return True
        else:
            return self.try_over_flow()

    def get_data_record_id(self) -> RecordID:
        return self.contents.get_data_record_id(self.current_slot)

    def delete(self, record_id: RecordID) -> None:
        while self.next():
            if self.get_data_record_id() == record_id:
                self.contents.delete(self.current_slot)
                return

    def insert(self, record_id: RecordID) -> DirectoryEntry | None:
        if (
            self.contents.get_flag() >= Node.VALID
            and self.contents.get_data_value(Slot.First).__lt__(self.search_key) > 0
        ):
            first_value = self.contents.get_data_value(Slot.First)
            new_block = self.contents.split(Slot.First, self.contents.get_flag())
            self.current_slot = Slot.First
            self.contents.set_flag(Node.OVERFLOW)
            self.contents.insert_leaf(self.current_slot, self.search_key, record_id)
            return DirectoryEntry(first_value, new_block.number())

        self.current_slot += 1
        self.contents.insert_leaf(self.current_slot, self.search_key, record_id)

        if not self.contents.is_full():
            return None

        first_key = self.contents.get_data_value(Slot.First)
        last_key = self.contents.get_data_value(self.contents.get_num_records() - 1)

        if first_key == last_key:

            new_block = self.contents.split(Slot.First, self.contents.get_flag())
            self.contents.set_flag(new_block.number())

            return None

        else:
            split_position = self.contents.get_num_records() // NODE_DIVISOR
            split_key = self.contents.get_data_value(split_position)

            if split_key == first_key:

                while self.contents.get_data_value(split_position) == split_key:
                    split_position += 1

                split_key = self.contents.get_data_value(split_position)

            else:
                while self.contents.get_data_value(split_position) == split_key:
                    split_position -= 1

            new_block = self.contents.split(split_position, Node.OVERFLOW)
            return DirectoryEntry(split_key, new_block.number())

    def try_over_flow(self) -> bool:
        first_key = self.contents.get_data_value(Slot.First)
        flag = self.contents.get_flag()

        if first_key != self.search_key or flag <= Node.OVERFLOW:
            return False

        self.contents.close()
        next_block = BlockID(self.file_name, flag)
        self.contents = BtreePage(self.transaction, next_block, self.layout)
        self.current_slot = Slot.First

        return True
