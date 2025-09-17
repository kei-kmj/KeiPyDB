from typing import Union


class Constant:

    def __init__(self, value: Union[int, str]) -> None:
        self.int_value = None
        self.str_value = None

        if isinstance(value, int):
            self.int_value = value

        elif isinstance(value, str):
            self.str_value = value

        else:
            raise ValueError("Unknown field type")

    def as_int(self) -> int:
        if self.int_value is None:
            raise TypeError("Constant does not hold an int")

        return self.int_value

    def as_string(self) -> str:
        if self.int_value is not None:
            return str(self.int_value)
        if self.str_value is None:
            raise ValueError("Constant does not hold a string")
        return self.str_value

    def is_int(self) -> bool:
        return self.int_value is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constant):
            return NotImplemented
        return self.int_value == other.int_value and self.str_value == other.str_value

    def __lt__(self, other: "Constant") -> bool:
        if self.int_value is not None and other.int_value is not None:
            return self.int_value < other.int_value
        elif self.str_value is not None and other.str_value is not None:
            return self.str_value < other.str_value
        else:
            raise TypeError("Cannot compare Constants of mismatched types")

    def __hash__(self) -> int:
        if self.int_value is not None:
            return hash(self.int_value)
        else:
            return hash(self.str_value)

    def __str__(self) -> str:
        """定数の値を文字列として返す"""
        if self.int_value is not None:
            return str(self.int_value)
        else:
            return self.str_value

    def __repr__(self) -> str:
        """デバッグ用の詳細な文字列表現を返す"""
        return f"Constant(value={self.int_value if self.int_value is not None else repr(self.str_value)})"
