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
        self.scan_left.next()
        self.scan_right.before_first()

    def get_int(self, field_name: str) -> int:
        """整数を取得（左スキャン優先）"""
        if self.scan_left.has_field(field_name):
            return self.scan_left.get_int(field_name)
        elif self.scan_right.has_field(field_name):
            return self.scan_right.get_int(field_name)
        elif field_name.startswith("right_") and self.scan_right.has_field(field_name[6:]):
            # right_プレフィックスを除去してチェック
            return self.scan_right.get_int(field_name[6:])
        else:
            available_fields = []
            if hasattr(self.scan_left, 'get_fields'):
                available_fields.extend(self.scan_left.get_fields())
            if hasattr(self.scan_right, 'get_fields'):
                available_fields.extend([f"right_{f}" for f in self.scan_right.get_fields()])
            raise ValueError(f"Field '{field_name}' not found. Available fields: {available_fields}")

    def get_string(self, field_name: str) -> str:
        """文字列を取得（左スキャン優先）"""
        if self.scan_left.has_field(field_name):
            return self.scan_left.get_string(field_name)
        elif self.scan_right.has_field(field_name):
            return self.scan_right.get_string(field_name)
        elif field_name.startswith("right_") and self.scan_right.has_field(field_name[6:]):
            # right_プレフィックスを除去してチェック
            return self.scan_right.get_string(field_name[6:])
        else:
            available_fields = []
            if hasattr(self.scan_left, 'get_fields'):
                available_fields.extend(self.scan_left.get_fields())
            if hasattr(self.scan_right, 'get_fields'):
                available_fields.extend([f"right_{f}" for f in self.scan_right.get_fields()])
            raise ValueError(f"Field '{field_name}' not found. Available fields: {available_fields}")

    def get_value(self, field_name: str) -> Constant:
        """値を取得（左スキャン優先）"""
        if self.scan_left.has_field(field_name):
            return self.scan_left.get_value(field_name)
        elif self.scan_right.has_field(field_name):
            return self.scan_right.get_value(field_name)
        elif field_name.startswith("right_") and self.scan_right.has_field(field_name[6:]):
            # right_プレフィックスを除去してチェック
            return self.scan_right.get_value(field_name[6:])
        else:
            available_fields = []
            if hasattr(self.scan_left, 'get_fields'):
                available_fields.extend(self.scan_left.get_fields())
            if hasattr(self.scan_right, 'get_fields'):
                available_fields.extend([f"right_{f}" for f in self.scan_right.get_fields()])
            raise ValueError(f"Field '{field_name}' not found. Available fields: {available_fields}")

    def next(self) -> bool:
        """次のレコードに進む"""
        if self.scan_right.next():
            return True
        elif self.scan_left.next():
            self.scan_right.before_first()
            return self.scan_right.next()
        else:
            return False

    def has_field(self, field_name: str) -> bool:
        """フィールドが存在するかどうか"""
        if self.scan_left.has_field(field_name) or self.scan_right.has_field(field_name):
            return True
        elif field_name.startswith("right_") and self.scan_right.has_field(field_name[6:]):
            return True
        return False

    def close(self) -> None:
        """クローズ"""
        self.scan_left.close()
        self.scan_right.close()
