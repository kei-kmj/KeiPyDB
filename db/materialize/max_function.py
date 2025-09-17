from abc import ABC
from typing import Optional

from db.materialize.aggregation_function import AggregationFunction
from db.query.constant import Constant
from db.query.scan import Scan


class MaxFunction(AggregationFunction, ABC):
    def __init__(self, field_name: str) -> None:
        self._field_name = field_name
        self.current_max: Optional[Constant] = None

    def process_first(self, scan: Scan) -> None:
        self.current_max = scan.get_value(self._field_name)

    def process_next(self, scan: Scan) -> None:
        new_value = scan.get_value(self._field_name)

        if self.current_max is None or new_value > self.current_max:
            self.current_max = new_value

    def field_name(self) -> str:
        return self._field_name

    def get_value(self) -> Constant:
        if self.current_max is None:
            raise RuntimeError("No max value")

        return self.current_max
