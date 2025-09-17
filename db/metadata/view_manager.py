from db.metadata.table_manager import TableManager
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class ViewManager:
    MAX_VIEW_DEF = 100

    def __init__(self, is_new: bool, table_manager: TableManager, transaction: Transaction) -> None:
        self.table_manager = table_manager
        if is_new:
            schema = Schema()
            schema.add_string_field("view_name", TableManager.MAX_NAME)
            schema.add_string_field("view_def", self.MAX_VIEW_DEF)
            self.table_manager.create_table("view_catalog", schema, transaction)

    def create_view(self, view_name: str, view_def: str, transaction: Transaction) -> None:
        """ビューを作成"""
        layout = self.table_manager.get_layout("view_catalog", transaction)
        table_scan = TableScan(transaction, "view_catalog", layout)
        table_scan.insert()
        table_scan.set_string("view_name", view_name)
        table_scan.set_string("view_def", view_def)
        table_scan.close()

    def get_view_def(self, view_name: str, transaction: Transaction) -> str | None:
        """指定されたビューの定義を取得"""
        result = None
        layout = self.table_manager.get_layout("view_catalog", transaction)
        table_scan = TableScan(transaction, "view_catalog", layout)

        while table_scan.next():
            if table_scan.get_string("view_name") == view_name:
                result = table_scan.get_string("view_def")

        table_scan.close()
        return result
