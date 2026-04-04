from db.materialize.limit_scan import LimitScan
from db.plan.plan import Plan
from db.query.scan import Scan
from db.record.schema import Schema


class LimitPlan(Plan):
    MAX_RUNS_FOR_MERGE = 2
    LIST_FIRST_INDEX = 0

    def __init__(self, source_plan: Plan, limit: int) -> None:
        super().__init__()
        self.source_plan = source_plan
        self.limit = limit

    def open(self) -> Scan:
        scan = self.source_plan.open()
        return LimitScan(scan, self.limit)

    def schema(self) -> Schema:
        return self.source_plan.schema()

    def distinct_values(self, field_name: str) -> int:
        return self.source_plan.distinct_values(field_name)

    def records_output(self) -> int:
        return min(self.limit, self.source_plan.records_output())

    def blocks_accessed(self) -> int:
        return self.source_plan.blocks_accessed()
