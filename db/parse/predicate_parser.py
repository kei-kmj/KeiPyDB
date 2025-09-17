from db.parse.lexer import Lexer


class PredicateParser:
    def __init__(self, predicate: str) -> None:
        self.lexer = Lexer(predicate)

    def field(self) -> str | None:
        """フィールドをパースして返す"""

        return self.lexer.eat_id()

    def constant(self) -> None:
        """定数をパースする"""
        if self.lexer.match_string_constant():
            self.lexer.eat_string_constant()
        else:
            self.lexer.eat_int_constant()

    def expression(self) -> None:
        """式をパースする"""
        if self.lexer.match_id():
            self.field()
        else:
            self.constant()

    def term(self) -> None:
        """項をパースする"""
        self.expression()
        self.lexer.eat_delimiter("=")
        self.expression()

    def predicate(self) -> None:
        """条件式をパースする"""
        self.term()

        if self.lexer.match_delimiter("and"):
            self.lexer.eat_keyword("and")
            self.term()
