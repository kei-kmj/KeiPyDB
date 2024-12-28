class Constant:
    def __init__(self, value: int | str) -> None:
        """値を指定してConstantを初期化"""
        if not isinstance(value, (int, str)):
            raise ValueError(f"value must be int or str, but got {type(value)}")
        self.value = value

    def __eq__(self, other: object) -> bool:
        """定数同士の透過性を比較"""
        if not isinstance(other, Constant):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """ハッシュ値を返す"""
        return hash(self.value)

    def __str__(self) -> str:
        """定数を文字列に変換"""
        return str(self.value)

    def as_int(self) -> int:
        """定数を整数として返す"""
        if isinstance(self.value, int):
            return self.value
        raise ValueError("Constant value is not an integer")

    def as_string(self) -> str:
        """定数を文字列として返す"""
        if isinstance(self.value, str):
            return self.value
        raise ValueError("Constant value is not a string")
