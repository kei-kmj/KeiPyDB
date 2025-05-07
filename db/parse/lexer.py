import re
from typing import Optional


class Lexer:
    def __init__(self, sql: str) -> None:
        """SQL文を解析するための字句解析器"""
        self.keywords = {
            "select",
            "from",
            "where",
            "and",
            "or",
            "not",
            "insert",
            "into",
            "values",
            "delete",
            "update",
            "set",
            "create",
            "table",
            "view",
            "drop",
            "index",
            "on",
            "primary",
            "key",
            "int",
            "char",
            "varchar",
            "text",
            "date",
            "time",
            "datetime",
            "null",
            "is",
            "like",
            "order",
            "by",
            "as",
            "inner",
            "left",
            "right",
            "outer",
            "join",
            "union",
            "all",
            "exists",
            "case",
            "when",
            "then",
            "else",
            "end",
            "in",
            "between",
            "exists",
            "limit",
            "offset",
        }
        self.tokens = self._tokenize(sql)
        self.current_token: Optional[str] = None
        self.next_token()

    def _tokenize(self, sql: str) -> list[str]:
        """SQL文をトークンに分割"""
        token_pattern = r"[a-zA-Z_][a-zA-Z_0-9]*|'[^']*'|\d+|[=,()<>*+-/]|."
        tokens = re.findall(token_pattern, sql.lower())

        return [token for token in tokens if not token.isspace()]

    def match_delimiter(self, delimiter: str) -> bool:
        """指定されたデリミタと現在のトークンが一致するかどうかを返す"""

        return self.current_token == delimiter.lower() or (delimiter == "*" and self.current_token == delimiter)

    def match_int_constant(self) -> bool:
        """現在のトークンが整数定数と一致するかどうかを返す"""
        if self.current_token is None:
            return False

        return self.current_token.isdigit()

    def match_string_constant(self) -> bool:
        """現在のトークンが文字列定数と一致するかどうかを返す"""

        if self.current_token is None:
            return False
        return self.current_token.startswith("'") and self.current_token.endswith("'")

    def match_keyword(self, keyword: str) -> bool:
        """指定されたキーワードと現在のトークンが一致するかどうかを返す"""
        return self.current_token.lower() == keyword.lower()

    def match_id(self) -> bool:
        """現在のトークンが識別子かどうかを返す"""
        if self.current_token is None:
            return False

        return self.current_token.isidentifier() and self.current_token not in self.keywords

    def eat_delimiter(self, delimiter: str) -> None:
        """指定されたデリミタを消費"""
        if not self.match_delimiter(delimiter):
            raise SyntaxError(f"Expected {delimiter}, but not found {self.current_token}")

        self.next_token()

    def eat_int_constant(self) -> int | None:
        """整数定数を消費"""
        if not self.current_token:
            raise SyntaxError(f"Expected integer constant, but not found {self.current_token}")

        value = int(self.current_token)
        self.next_token()
        return value

    def eat_string_constant(self) -> str | None:
        """文字列定数を消費"""

        value = self.current_token
        self.next_token()
        return value

    def eat_keyword(self, keyword: str) -> None:
        """指定されたキーワードを消費"""
        if self.current_token.lower() != keyword.lower():
            raise SyntaxError(f"Expected {keyword}, but not found {self.current_token}")

        self.next_token()

    def eat_id(self) -> str:
        """識別子を消費"""
        if not self.current_token:
            raise SyntaxError(f"Expected identifier, but not found {self.current_token}")

        value = self.current_token
        self.next_token()
        return value

    def next_token(self) -> None:
        """次のトークンに進む"""
        try:
            self.current_token = self.tokens.pop(0)
        except IndexError:
            self.current_token = None
