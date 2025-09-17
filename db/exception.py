class BadSyntaxException(Exception):
    """誤った構文が含まれている場合に発生する例外"""

    def __init__(self, message: str = "Query has incorrect syntax") -> None:
        super().__init__(message)
