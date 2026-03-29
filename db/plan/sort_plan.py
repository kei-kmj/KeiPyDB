from db.materialize.sort_scan import SortScan
from db.plan.plan import Plan


class SortPlan(Plan):

    def __init__(self, plan: Plan, order_by: list[str]) -> None:
        super().__init__()
        self.plan = plan
        self.order_by = order_by

    def open(self):
        scan = self.plan.open()
        records = []
        while scan.next():
            row = {field: scan.get_value(field) for field in self.plan.schema().get_fields()}
            records.append(row)
        scan.close()
        records.sort(key=lambda r: tuple(r[field] for field in self.order_by))
        return SortScan(records, self.plan.schema())

    def blocks_accessed(self) -> int:
        return self.plan.blocks_accessed()

    def records_output(self) -> int:
        return self.plan.records_output()

    def distinct_values(self, field_name: str) -> int:
        return self.plan.distinct_values(field_name)

    def schema(self):
        return self.plan.schema()