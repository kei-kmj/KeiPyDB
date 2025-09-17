from db.query.scan import Scan


class RecordComparator:
    def __init__(self, sort_fields: list[str]) -> None:
        self.sort_fields = sort_fields

    def compare(self, scan_first: Scan, scan_second: Scan) -> int:

        for field_name in self.sort_fields:
            val_first = scan_first.get_value(field_name)
            val_second = scan_second.get_value(field_name)

            result = val_first.__lt__(val_second)

            return result

        return 0
