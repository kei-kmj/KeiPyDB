from typing import Dict

from db.metadata.index_info import IndexInfo
from db.metadata.index_manager import IndexManager
from db.metadata.stat_info import StatInfo
from db.metadata.stat_manager import StatManager
from db.metadata.table_manager import TableManager
from db.metadata.view_manager import ViewManager
from db.record.layout import Layout
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class MetadataManager:
    def __init__(self, is_new: bool, transaction: Transaction) -> None:
        self.table_manager = TableManager(is_new, transaction)
        self.view_manager = ViewManager(is_new, self.table_manager, transaction)
        self.stat_manager = StatManager(self.table_manager, transaction)
        self.index_manager = IndexManager(is_new, self.table_manager, self.stat_manager, transaction)

    def create_table(self, table_name: str, schema: Schema, transaction: Transaction) -> None:
        self.table_manager.create_table(table_name, schema, transaction)

    def get_layout(self, table_name: str, transaction: Transaction) -> Layout:
        return self.table_manager.get_layout(table_name, transaction)

    def create_view(self, view_name: str, view_definition: str, transaction: Transaction) -> None:
        self.view_manager.create_view(view_name, view_definition, transaction)

    def get_view_definition(self, view_name: str, transaction: Transaction) -> str | None:
        return self.view_manager.get_view_def(view_name, transaction)

    def create_index(self, index_name: str, table_name: str, field_name: str, transaction: Transaction) -> None:
        self.index_manager.create_index(index_name, table_name, field_name, transaction)

    def get_index_info(self, table_name: str, transaction: Transaction) -> Dict[str, IndexInfo]:
        return self.index_manager.get_index_info(table_name, transaction)

    def get_stat_info(self, table_name: str,transaction: Transaction) -> StatInfo:

        return self.stat_manager.get_stat_info(table_name, transaction)
