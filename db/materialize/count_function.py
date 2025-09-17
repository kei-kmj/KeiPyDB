from abc import ABC

from db.materialize.aggregation_function import AggregationFunction
from db.query.constant import Constant
from db.query.scan import Scan


class CountFunction(AggregationFunction, ABC):
    def __init__(self, field_name: str) -> None:
        self._field_name = field_name
        self._count = 0

    def process_first(self, scan: Scan) -> None:
        self._count = 1

    def process_next(self, scan: Scan) -> None:
        self._count += 1

    def field_name(self) -> str:
        return "countof" + self._field_name

    def get_value(self) -> Constant:
        return Constant(self._count)
