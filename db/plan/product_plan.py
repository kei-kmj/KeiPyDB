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
        self.schema_obj = Schema()
        self.schema_obj.add_all(left_plan.schema())
        self.schema_obj.add_all(right_plan.schema())

    def open(self) -> Scan:

        scan_left = self.plan_left.open()
        scan_right = self.plan_right.open()

        return ProductScan(scan_left, scan_right)

    def block_accessed(self) -> int:
        return self.plan_left.block_accessed() + (self.plan_right.record_output() * self.plan_left.block_accessed())

    def record_output(self) -> int:

        return self.plan_left.record_output() * self.plan_right.record_output()

    def distinct_values(self, field_name: str) -> int:
        if self.schema_obj.has_field(field_name):
            return self.plan_left.distinct_values(field_name)
        else:
            return self.plan_right.distinct_values(field_name)

    def schema(self) -> Schema:
        return self.schema_obj
