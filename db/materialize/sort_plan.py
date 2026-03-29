from abc import ABC

from db.materialize.materialize_plan import MaterializePlan
from db.materialize.record_comparator import RecordComparator
from db.materialize.sort_scan import SortScan
from db.materialize.temp_table import TempTable
from db.plan.plan import Plan
from db.query.scan import Scan
from db.query.update_scan import UpdateScan
from db.record.schema import Schema
from db.transaction.transaction import Transaction


class SortPlan(Plan, ABC):
    MAX_RUNS_FOR_MERGE = 2
    LIST_FIRST_INDEX = 0

    def __init__(self, transaction: Transaction, source_plan: Plan, sort_fields: list[str]) -> None:
        super().__init__()
        self.transaction = transaction
        self.source_plan = source_plan
        self._schema = self.source_plan.schema()
        self.comparator = RecordComparator(sort_fields)

    def open(self) -> Scan:
        source_scan = self.source_plan.open()
        runs = self._split_into_runs(source_scan)
        source_scan.close()

        while len(runs) > self.MAX_RUNS_FOR_MERGE:
            runs = self._do_a_merge_iteration(runs)

        return SortScan(runs, self.comparator)

    def _split_into_runs(self, source_scan: Scan) -> list[TempTable]:
        schema = self.source_plan.schema()
        records = []

        while source_scan.next():
            row = {field: source_scan.get_value(field) for field in schema.get_fields()}
            records.append(row)

        records.sort(key=lambda r: self.comparator.compare_row(r))

        run = TempTable(self.transaction, schema)
        dest = run.open()
        for record in records:
            dest.insert()
            for field_name in schema.get_fields():
                dest.set_value(field_name, record[field_name])

        dest.close()
        return [run]

    def _do_a_merge_iteration(self, runs: list[TempTable]) -> list[TempTable]:
        result = []

        while len(runs) > self.LIST_FIRST_INDEX + 1:
            left = runs.pop(self.LIST_FIRST_INDEX)
            right = runs.pop(self.LIST_FIRST_INDEX)
            result.append(self._merge_two_runs(left, right))

        if len(runs) == self.LIST_FIRST_INDEX + 1:
            result.append(runs[self.LIST_FIRST_INDEX])

        return result

    def _merge_two_runs(self, left: TempTable, right: TempTable) -> TempTable:
        source_left = left.open()
        source_right = right.open()

        result_temp_table = TempTable(self.transaction, self._schema)
        dest_scan = result_temp_table.open()

        has_more_left = source_left.next()
        has_more_right = source_right.next()

        while has_more_left and has_more_right:
            if self.comparator.compare(source_left, source_right) < 0:
                has_more_left = self._copy(source_left, dest_scan)
            else:
                has_more_right = self._copy(source_right, dest_scan)

        while has_more_left:
            has_more_left = self._copy(source_left, dest_scan)

        while has_more_right:
            has_more_right = self._copy(source_right, dest_scan)

        source_left.close()
        source_right.close()
        dest_scan.before_first()

        return result_temp_table

    def _copy(self, source: Scan, dest_scan: UpdateScan) -> bool:
        dest_scan.insert()
        for field_name in self._schema.get_fields():
            dest_scan.set_value(field_name, source.get_value(field_name))
        return source.next()

    def schema(self) -> Schema:
        return self.source_plan.schema()

    def distinct_values(self, field_name: str) -> int:
        return self.source_plan.distinct_values(field_name)

    def records_output(self) -> int:
        return self.source_plan.records_output()

    def blocks_accessed(self) -> int:

        materialized_plan = MaterializePlan(self.transaction, self.source_plan)
        return materialized_plan.blocks_accessed()
