from typing import Dict

from db.metadata.index_info import IndexInfo
from db.metadata.stat_manager import StatManager
from db.metadata.table_manager import TableManager
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class IndexManager:
    def __init__(
        self, is_new: bool, table_manager: TableManager, stat_manager: StatManager, transaction: Transaction
    ) -> None:

        if is_new:
            schema = Schema()
            schema.add_string_field("index_name", TableManager.MAX_NAME)
            schema.add_string_field("table_name", TableManager.MAX_NAME)
            schema.add_string_field("field_name", TableManager.MAX_NAME)
            table_manager.create_table("index_catalog", schema, transaction)

        self.table_manager = table_manager
        self.stat_manager = stat_manager
        self.layout = table_manager.get_layout("index_catalog", transaction)

    def create_index(self, index_name: str, table_name: str, field_name: str, transaction: Transaction) -> None:
        """インデックスを作成"""
        table_scan = TableScan(transaction, "index_catalog", self.layout)
        table_scan.insert()
        table_scan.set_string("index_name", index_name)
        table_scan.set_string("table_name", table_name)
        table_scan.set_string("field_name", field_name)
        table_scan.close()

        # 2. 実際のインデックス構造を作成
        table_layout = self.table_manager.get_layout(table_name, transaction)
        stat_info = self.stat_manager.get_stat_info(table_name, transaction)
        index_info = IndexInfo(index_name, field_name, table_layout.schema, stat_info)
        hash_index = index_info.open(transaction)

        # 3. 既存のデータでインデックスを埋める
        data_scan = TableScan(transaction, table_name, table_layout)
        while data_scan.next():
            dataval = data_scan.get_value(field_name)
            rid = data_scan.get_rid()
            hash_index.insert(dataval, rid)
        data_scan.close()
        hash_index.close()

    def get_index_info(self, table_name: str, transaction: Transaction) -> Dict[str, IndexInfo]:

        result: Dict[str, IndexInfo] = {}
        table_scan = TableScan(transaction, "index_catalog", self.layout)

        while table_scan.next():
            if table_scan.get_string("table_name") == table_name:
                index_name = table_scan.get_string("index_name")
                field_name = table_scan.get_string("field_name")
                table_layout = self.table_manager.get_layout(table_name, transaction)
                stat_info = self.stat_manager.get_stat_info(table_name, transaction)
                index_info = IndexInfo(index_name, field_name, table_layout.get_schema(), stat_info)
                result[field_name] = index_info

        table_scan.close()
        return result
