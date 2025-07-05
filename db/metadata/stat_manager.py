from threading import Lock
from typing import Dict

from db.metadata.stat_info import StatInfo
from db.metadata.table_manager import TableManager
from db.record.layout import Layout
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class StatManager:
    def __init__(self, table_manager: TableManager, transaction: Transaction) -> None:
        self.table_manager = table_manager
        self.table_stats: Dict[str, StatInfo] = {}
        self.num_calls = 0
        self.lock = Lock()
        self.refresh_statistics(transaction)

    def get_stat_info(self, table_name: str, transaction: Transaction) -> StatInfo:
        """指定されたテーブルの統計情報を取得"""

        layout = self.table_manager.get_layout(table_name, transaction)

        if layout is None:
            return StatInfo(0, 0)  # テーブルが存在しない場合は空の統計情報を返す

        with self.lock:
            self.num_calls += 1
            if self.num_calls > 100:
                self.refresh_statistics(transaction)
            if table_name not in self.table_stats:
                self.table_stats[table_name] = self._calculate_table_stats(table_name, layout, transaction)
            return self.table_stats[table_name]

    def refresh_statistics(self, transaction: Transaction) -> None:
        """テーブルの統計情報を更新"""
        with self.lock:
            self.table_stats = {}
            self.num_calls = 0
            table_catalog_layout = self.table_manager.get_layout("table_catalog", transaction)
            table_scan = TableScan(transaction, "table_catalog", table_catalog_layout)

            while table_scan.next():
                table_name = table_scan.get_string("table_name")
                layout = self.table_manager.get_layout(table_name, transaction)
                self.table_stats[table_name] = self._calculate_table_stats(table_name, layout, transaction)

            table_scan.close()

    def _calculate_table_stats(self, table_name: str, layout: Layout, transaction: Transaction) -> StatInfo:

        if layout is None:
            return StatInfo(0, 0)

        num_records = 0
        num_blocks = 0
        table_scan = TableScan(transaction, table_name, layout)

        while table_scan.next():
            num_records += 1
            num_blocks = max(num_blocks, table_scan.get_rid().block_number + 1)

        table_scan.close()
        return StatInfo(num_blocks, num_records)
