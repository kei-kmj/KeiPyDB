from abc import ABC

from db.plan.plan import Plan
from db.query.product_scan import ProductScan
from db.query.scan import Scan
from db.record.schema import Schema


class ProductPlan(Plan, ABC):

    def __init__(self, left_plan: Plan, right_plan: Plan) -> None:
        super().__init__()
        self.plan_left = left_plan
        self.plan_right = right_plan
        self._schema = None  # 遅延初期化のため

    def open(self) -> Scan:

        scan_left = self.plan_left.open()
        scan_right = self.plan_right.open()

        return ProductScan(scan_left, scan_right)

    def blocks_accessed(self) -> int:
        return self.plan_left.blocks_accessed() + (self.plan_right.records_output() * self.plan_left.blocks_accessed())

    def records_output(self) -> int:

        return self.plan_left.records_output() * self.plan_right.records_output()

    def distinct_values(self, field_name: str) -> int:
        if self.plan_left.schema().has_field(field_name):
            left_distinct = self.plan_left.distinct_values(field_name)
            if self.plan_right.schema().has_field(field_name):
                # フィールドが両方のスキーマに存在
                right_distinct = self.plan_right.distinct_values(field_name)
                # 保守的に最大値を返す
                return max(left_distinct, right_distinct)
            return left_distinct
        elif self.plan_right.schema().has_field(field_name):
            return self.plan_right.distinct_values(field_name)
        else:
            raise ValueError(f"フィールド '{field_name}' はどちらのスキーマにも見つかりません")

    def schema(self) -> Schema:
        # スキーマを一度だけ計算して保持
        if self._schema is None:
            self._schema = Schema()

            # 左スキーマのフィールドを最初に追加
            for field_name in self.plan_left.schema().fields:
                field_info = self.plan_left.schema().info[field_name]
                self._schema.add_field(field_name, field_info.field_type, field_info.length)

            # 右スキーマのフィールドを衝突検出と共に追加
            for field_name in self.plan_right.schema().fields:
                if field_name not in self._schema.fields:
                    field_info = self.plan_right.schema().info[field_name]
                    self._schema.add_field(field_name, field_info.field_type, field_info.length)
                else:
                    # 衝突を避けるためテーブルプレフィックスを付けて追加
                    prefixed_name = f"right_{field_name}"
                    field_info = self.plan_right.schema().info[field_name]
                    self._schema.add_field(prefixed_name, field_info.field_type, field_info.length)

        return self._schema
