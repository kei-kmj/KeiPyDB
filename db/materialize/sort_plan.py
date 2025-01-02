from abc import ABC

from db.materialize.record_comparator import RecordComparator
from db.materialize.temp_table import TempTable
from db.plan.plan import Plan
from db.query.scan import Scan
from db.query.update_scan import UpdateScan
from db.transaction.transaction import Transaction


class SortPlan(Plan, ABC):
    def __init__(self, transaction: Transaction, plan: Plan, sort_fields: list[str]) -> None:
        super().__init__()
        self.transaction = transaction
        self.plan = plan
        self._schema = self.plan.schema()
        self.comparator = RecordComparator(sort_fields)

    def open(self) -> Scan:
        source_scan = self.plan.open()
        runs = self._split_into_runs(source_scan)
        source_scan.close()

        while len(runs) > 2:
            runs = self._do_a_merge_iteration(runs)

        return SortScan(runs, self.comparator)

    def _split_into_runs(self, source_scan: Scan) -> list[TempTable]:
        temp_tables = []
        source_scan.before_first()

        if not source_scan.next():
            return temp_tables

        current_temp_table = TempTable(self.transaction, self._schema)
        temp_tables.append(current_temp_table)
        current_scan = current_temp_table.open()

        while self._copy(source_scan, current_scan):
            if self.comparator.compare(source_scan, current_scan) < 0:
                current_scan.close()
                current_temp_table = TempTable(self.transaction, self._schema)
                temp_tables.append(current_temp_table)
                current_scan = current_temp_table.open()

        current_scan.close()
        return temp_tables

    def _do_a_merge_iteration(self, runs: list[TempTable]) -> list[TempTable]:
        result = []

        while len(runs) > 1:
            left = runs.pop(0)
            right = runs.pop(0)
            result.append(self._merge_two_runs(left, right))

        if len(runs) == 1:
            result.append(runs[0])

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
            dest_scan.set_val(field_name, source.get_val(field_name))
        return source.next()

