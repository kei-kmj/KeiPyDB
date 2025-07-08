import math
from typing import Optional

from db.constants import FieldType, Node, Slot
from db.file.block_id import BlockID
from db.index.btree.btree_dir import BtreeDir
from db.index.btree.btree_leaf import BtreeLeaf
from db.index.btree.btree_page import BtreePage
from db.query.constant import Constant
from db.record.layout import Layout
from db.record.record_id import RecordID
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class BtreeIndex:
    BASE_SEARCH_COST = 1
    ROOT_BLOCK_INDEX = 0
    EMPTY = 0

    def __init__(self, transaction: Transaction, index_name: str, leaf_layout: Layout) -> None:
        self.transaction = transaction
        self.leaf_table = index_name + "leaf"
        self.leaf_layout = leaf_layout
        self.leaf: Optional[BtreeLeaf] = None

        if self.transaction.size(self.leaf_table) == self.EMPTY:
            block = self.transaction.append(self.leaf_table)
            node = BtreePage(self.transaction, block, leaf_layout)
            node.format(block, Node.Valid)

        dir_schema = Schema()
        block_field_type = self.leaf_layout.get_schema().get_type("block")
        data_value_field_type = self.leaf_layout.get_schema().get_type("data_value")

        dir_schema.add_field("block", block_field_type, 0)
        dir_schema.add_field("data_value", data_value_field_type, 0)

        dir_table = index_name + "dir"
        self.dir_layout = Layout(dir_schema)
        self.root_block = BlockID(dir_table, self.ROOT_BLOCK_INDEX)

        if self.transaction.size(dir_table) == self.EMPTY:
            self.transaction.append(dir_table)
            root = BtreePage(self.transaction, self.root_block, self.dir_layout)
            root.format(self.root_block, Node.Valid)

            field_type = dir_schema.get_type("data_value")
            min_value = Constant(int("-inf")) if field_type == FieldType.Integer else Constant("")

            first_leaf_block = 0
            root.insert_directory(Slot.First, min_value, first_leaf_block)
            root.close()

    def before_first(self, search_key: Constant) -> None:
        self.close()

        root = BtreeDir(self.transaction, self.root_block, self.dir_layout)
        block_number = root.search(search_key)
        root.close()
        leaf_block = BlockID(self.leaf_table, block_number)

        self.leaf = BtreeLeaf(self.transaction, leaf_block, self.leaf_layout, search_key)

    def next(self) -> bool:
        if self.leaf:
            return self.leaf.next()
        return False

    def get_data_record_id(self) -> RecordID:
        if self.leaf:
            return self.leaf.get_data_record_id()
        raise RuntimeError("No leaf page open")

    def insert(self, data_value: Constant, record_id: RecordID) -> None:
        self.before_first(data_value)

        if not self.leaf:
            return

        dir_entry = self.leaf.insert(record_id)
        self.leaf.close()

        if dir_entry is None:
            return

        root = BtreeDir(self.transaction, self.root_block, self.dir_layout)
        split_entry = root.insert(dir_entry)

        if split_entry:
            root.make_new_root(split_entry)

        root.close()

    def delete(self, data_value: Constant, record_id: RecordID) -> None:
        if not self.leaf:
            return

        self.before_first(data_value)
        self.leaf.delete(record_id)
        self.leaf.close()

    def close(self) -> None:
        if self.leaf:
            self.leaf.close()
            self.leaf = None

    def search_cost(self, num_blocks: int, records_per_block: int) -> int:
        return self.BASE_SEARCH_COST + int(math.log(num_blocks, records_per_block))
