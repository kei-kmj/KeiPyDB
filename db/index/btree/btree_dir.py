from db.constants import Slot, NODE_DIVISOR
from db.file.block_id import BlockID
from db.index.btree.btree_page import BtreePage
from db.index.btree.dir_entry import DirectoryEntry
from db.query.constant import Constant
from db.record.layout import Layout
from db.transaction.transaction import Transaction


class BtreeDir:
    NEXT_LEVEL = 1
    LEAF_NODE = 0
    INSERT_OFFSET = 1

    def __init__(self, transaction: Transaction, block: BlockID, layout: Layout) -> None:
        self.transaction = transaction
        self.layout = layout
        self.contents = BtreePage(transaction, block, layout)
        self.file_name = block.file_name

    def close(self) -> None:
        self.contents.close()

    def search(self, search_key: Constant) -> int:
        child_block = self.find_child_block(search_key)

        while self.contents.get_flag() > self.LEAF_NODE:
            self.contents.close()
            self.contents = BtreePage(self.transaction, child_block, self.layout)
            child_block = self.find_child_block(search_key)

        return child_block.number()

    def find_child_block(self, search_key: Constant) -> BlockID:
        slot = self.contents.find_slot_before(search_key)

        if self.contents.get_data_value(slot + self.NEXT_LEVEL) == search_key:
            slot += 1

        block_number = self.contents.get_child_number(slot)

        return BlockID(self.file_name, block_number)

    def make_new_root(self, dir_entry: DirectoryEntry) -> None:
        first_value = self.contents.get_data_value(Slot.First)
        level = self.contents.get_flag()
        new_block = self.contents.split(Slot.First, level)
        old_root = DirectoryEntry(first_value, new_block.number())
        self.insert_entry(old_root)
        self.insert_entry(dir_entry)
        self.contents.set_flag(level + self.NEXT_LEVEL)

    def insert(self, dir_entry: DirectoryEntry) -> DirectoryEntry | None:
        if self.contents.get_flag() == self.LEAF_NODE:
            self.insert_entry(dir_entry)

        chile_block = self.find_child_block(dir_entry.data_value)
        child_dir = BtreeDir(self.transaction, chile_block, self.layout)
        my_entry = child_dir.insert(dir_entry)
        child_dir.close()

        return self.insert_entry(my_entry) if my_entry else None

    def insert_entry(self, dir_entry: DirectoryEntry) -> DirectoryEntry | None:
        new_slot = self.INSERT_OFFSET + self.contents.find_slot_before(dir_entry.data_value)
        self.contents.insert_directory(new_slot, dir_entry.data_value, dir_entry.block_number)

        if not self.contents.is_full():
            return None

        level = self.contents.get_flag()
        split_position = self.contents.get_num_records() // NODE_DIVISOR
        split_value = self.contents.get_data_value(split_position)
        new_block = self.contents.split(split_position, level)
        return DirectoryEntry(split_value, new_block.number())
