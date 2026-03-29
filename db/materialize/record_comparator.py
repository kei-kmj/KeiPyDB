from db.query.scan import Scan


class RecordComparator:
    def __init__(self, sort_fields: list[str]) -> None:
        self.sort_fields = sort_fields

    def compare(self, scan_first: Scan, scan_second: Scan) -> int:

        for field_name in self.sort_fields:
            val_first = scan_first.get_value(field_name)
            val_second = scan_second.get_value(field_name)

            if val_first < val_second:
                return -1
            elif val_first > val_second:
                return 1

        return 0


    def compare_row(self, row:dict) -> tuple:
        return tuple(row[field] for field in self.sort_fields)
