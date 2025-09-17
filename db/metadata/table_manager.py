from db.record.layout import Layout
from db.record.schema import Schema
from db.record.table_scan import TableScan
from db.transaction.transaction import Transaction


class TableManager:
    MAX_NAME = 16

    def __init__(self, is_new: bool, transaction: Transaction) -> None:
        table_catalog_schema = Schema()
        table_catalog_schema.add_string_field("table_name", self.MAX_NAME)
        table_catalog_schema.add_int_field("slot_size")
        self.table_catalog_layout = Layout(table_catalog_schema)

        field_catalog_schema = Schema()
        field_catalog_schema.add_string_field("table_name", self.MAX_NAME)
        field_catalog_schema.add_string_field("field_name", self.MAX_NAME)
        field_catalog_schema.add_int_field("type")
        field_catalog_schema.add_int_field("length")
        field_catalog_schema.add_int_field("offset")
        self.field_catalog_layout = Layout(field_catalog_schema)

        if is_new:
            self.create_table("table_catalog", table_catalog_schema, transaction)
            self.create_table("field_catalog", field_catalog_schema, transaction)

            transaction.commit()

    def create_table(self, table_name: str, schema: Schema, transaction: Transaction) -> None:
        """新しいテーブルを作成"""
        layout = Layout(schema)
        table_catalog = TableScan(transaction, "table_catalog", self.table_catalog_layout)
        table_catalog.insert()
        table_catalog.set_string("table_name", table_name)
        table_catalog.set_int("slot_size", layout.get_slot_size())
        table_catalog.close()

        field_catalog = TableScan(transaction, "field_catalog", self.field_catalog_layout)

        for field_name in schema.get_fields():
            field_catalog.insert()
            field_catalog.set_string("table_name", table_name)
            field_catalog.set_string("field_name", field_name)
            field_catalog.set_int("type", schema.get_type(field_name))
            field_catalog.set_int("length", schema.get_length(field_name))
            field_catalog.set_int("offset", layout.get_offset(field_name))

        field_catalog.close()

    def get_layout(self, table_name: str, transaction: Transaction) -> Layout:
        """指定されたテーブルのレイアウトをカタログから取得"""
        size = -1

        # テーブルカタログからスロットサイズを取得
        table_catalog = TableScan(transaction, "table_catalog", self.table_catalog_layout)
        while table_catalog.next():
            if table_catalog.get_string("table_name") == table_name:
                size = table_catalog.get_int("slot_size")
                break
        table_catalog.close()

        # field_catalogからフィールド情報を取得
        schema = Schema()
        offsets: dict[str, int] = {}
        field_catalog = TableScan(transaction, "field_catalog", self.field_catalog_layout)
        while field_catalog.next():
            name = field_catalog.get_string("table_name")

            if name == table_name:
                field_name = field_catalog.get_string("field_name")

                field_type = field_catalog.get_int("type")
                length = field_catalog.get_int("length")
                offset = field_catalog.get_int("offset")
                offsets[field_name] = offset
                schema.add_field(field_name, field_type, length)

        field_catalog.close()

        return Layout(schema, offsets, size)
