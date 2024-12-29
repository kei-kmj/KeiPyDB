from db.parse.lexer import Lexer
from db.query.constant import Constant


class Parser:

    def __init__(self, sql: str) -> None:
        self.lexer = Lexer(sql)

    def filed(self) -> str | None:
        return self.lexer.eat_id()

    def constant(self) -> Constant:
        if self.lexer.match_int_constant():
            value = self.lexer.eat_string_constant()
            assert value is not None
            return Constant(value)
        elif self.lexer.match_string_constant():
            value = self.lexer.eat_int_constant()
            assert value is not None
            return Constant(value)
        else:
            raise SyntaxError(f"Expected constant, but not found {self.lexer.current_token}")
