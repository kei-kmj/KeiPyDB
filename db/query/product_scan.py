from abc import ABC

from db.query.constant import Constant
from db.query.scan import Scan


class ProductScan(Scan, ABC):
    def __init__(self, scan_left: Scan, scan_right: Scan) -> None:
        """２つのscanの直積を行うスキャンを作成"""
        self.scan_left = scan_left
        self.scan_right = scan_right
        self.before_first()

    def before_first(self) -> None:
        """最初のレコードに戻る"""
        self.scan_left.before_first()
        self.scan_right.next()
        self.scan_right.before_first()

    def next(self) -> bool:
        """次のレコードに進む"""
        if self.scan_right.next():
            return True
        else:
            self.scan_right.before_first()
            return self.scan_left.next() and self.scan_right.next()

    def get_int(self, field_name: str) -> int:
        """整数を取得"""
        if self.has_field(field_name):
            return self.scan_left.get_int(field_name)
        else:
            return self.scan_right.get_int(field_name)

    def get_string(self, field_name: str) -> str:
        """文字列を取得"""
        if self.has_field(field_name):
            return self.scan_left.get_string(field_name)
        else:
            return self.scan_right.get_string(field_name)

    def get_val(self, field_name: str) -> int | str | Constant:
        """値を取得"""
        if self.has_field(field_name):
            return self.scan_left.get_val(field_name)
        else:
            return self.scan_right.get_val(field_name)

    def has_field(self, field_name: str) -> bool:
        """フィールドが存在するかどうか"""
        return self.scan_left.has_field(field_name) or self.scan_right.has_field(field_name)

    def close(self) -> None:
        """クローズ"""
        self.scan_left.close()
        self.scan_right.close()
