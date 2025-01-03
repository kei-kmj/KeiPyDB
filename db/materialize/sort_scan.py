from abc import ABC
from typing import List, Optional

from db.materialize.record_comparator import RecordComparator
from db.materialize.temp_table import TempTable
from db.query.constant import Constant
from db.query.scan import Scan
from db.query.update_scan import UpdateScan
from db.record.record_id import RecordID


class SortScan(Scan, ABC):

    def __init__(self, runs: List[TempTable], comparator: RecordComparator) -> None:
        sorted_first = runs[0].open()
        sorted_second = runs[1].open() if len(runs) > 1 else None
        self.scan_first = sorted_first
        self.scan_second: Optional[UpdateScan] = sorted_second
        self.current_scan: Optional[UpdateScan] = None
        self.comparator = comparator

        self.has_more_first = self.scan_first.next()
        self.has_more_second = self.scan_second.next() if self.scan_second else False
        self.saved_position: List[Optional[RecordID]] = []

    def before_first(self) -> None:
        self.current_scan = None
        self.scan_first.before_first()
        self.has_more_first = self.scan_first.next()

        if self.scan_second:
            self.scan_second.before_first()
            self.has_more_second = self.scan_second.next()

    def next(self) -> bool:

        if self.current_scan:
            if self.current_scan == self.scan_first:
                self.has_more_first = self.scan_first.next()
            elif self.current_scan == self.scan_second:
                self.has_more_second = self.scan_second.next()

        if not self.has_more_first and not self.has_more_second:
            return False

        if not self.has_more_first and not self.has_more_second:
            return False

        if self.has_more_first and self.has_more_second:
            if self.scan_first and self.scan_second:
                self.current_scan = (
                    self.scan_first
                    if self.comparator.compare(self.scan_first, self.scan_second) < 0
                    else self.scan_second
                )

        elif self.has_more_first:
            self.current_scan = self.scan_first
        elif self.has_more_second:
            self.current_scan = self.scan_second

        return True

    def close(self) -> None:
        self.scan_first.close()
        if self.scan_second:
            self.scan_second.close()

    def get_value(self, field: str) -> Constant:

        if self.current_scan:
            return self.current_scan.get_value(field)

        raise RuntimeError("No current scan is selected")

    def get_int(self, field_name: str) -> int:
        if self.current_scan:
            return self.current_scan.get_int(field_name)

        raise RuntimeError("No current scan is selected")

    def get_string(self, field_name: str) -> str:

        if self.current_scan:
            return self.current_scan.get_string(field_name)

        raise RuntimeError("No current scan is selected")

    def has_field(self, field_name: str) -> bool:

        if self.current_scan:
            return self.current_scan.has_field(field_name)

        raise RuntimeError("No current scan is selected")

    def save_position(self) -> None:

        record_id_first = self.scan_first.get_rid()
        record_id_second = self.scan_second.get_rid() if self.scan_second else None

        self.saved_position = [record_id_first, record_id_second]

    def restore_position(self) -> None:

        if not self.saved_position:
            raise RuntimeError("No position saved")

        first_position = self.saved_position[0]
        second_position = self.saved_position[1]

        if first_position is not None:
            self.scan_first.move_to_rid(first_position)

        if self.scan_second and first_position and second_position:
            self.scan_second.move_to_rid(first_position)
