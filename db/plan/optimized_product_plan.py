from abc import ABC

from db.plan.plan import Plan
from db.plan.product_plan import ProductPlan
from db.query.scan import Scan
from db.record.schema import Schema


class OptimizedProductPlan(Plan, ABC):
    def __init__(self, plan_first: Plan, plan_second: Plan) -> None:
        super().__init__()
        self.product_first = ProductPlan(plan_first, plan_second)
        self.product_second = ProductPlan(plan_second, plan_first)

        self.block_first = self.product_first.block_accessed()
        self.block_second = self.product_second.block_accessed()
        self.best_plan: Plan = self.product_first if self.block_first < self.block_second else self.product_second

    def open(self) -> Scan:
        return self.best_plan.open()

    def block_accessed(self) -> int:
        return self.best_plan.block_accessed()

    def record_output(self) -> int:
        return self.best_plan.record_output()

    def distinct_values(self, field_name: str) -> int:
        return self.best_plan.distinct_values(field_name)

    def schema(self) -> Schema:
        return self.best_plan.schema()
