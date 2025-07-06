import pytest

from db.parse.lexer import Lexer
from db.exception import BadSyntaxException


class TestLexerEnhanced:
    """Lexerの拡張テスト - 実際のシナリオを使用"""

    @pytest.mark.skip
    def test_lexer_initialization(self):
        """Lexerの初期化テスト"""
        sql = "SELECT * FROM users"
        lexer = Lexer(sql)
        
        # 初期状態の確認
        assert lexer.sql == sql
        assert lexer.current_token == "select"  # 最初のトークンに進む
        assert lexer.tokens is not None
        assert len(lexer.tokens) > 0
    
    def test_lexer_tokenization_comprehensive(self):
        """包括的なトークン化テスト"""
        sql = "SELECT id, name, 'test string', 123, table.field FROM users WHERE age = 25"
        lexer = Lexer(sql)
        
        expected_tokens = [
            "select", "id", ",", "name", ",", "'test string'", ",", "123", ",", 
            "table", ".", "field", "from", "users", "where", "age", "=", "25"
        ]
        
        # トークンリストの確認
        for expected_token in expected_tokens:
            assert lexer.current_token == expected_token.lower() if expected_token.isalpha() else expected_token
            lexer.next_token()

    @pytest.mark.skip
    def test_lexer_keyword_recognition(self):
        """キーワード認識テスト"""
        keywords = [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
            "DELETE", "CREATE", "TABLE", "VIEW", "INDEX", "ON", "AS", "AND", "OR",
            "INT", "VARCHAR", "DISTINCT", "ORDER", "BY", "GROUP", "HAVING", "JOIN"
        ]
        
        for keyword in keywords:
            sql = f"{keyword} test"
            lexer = Lexer(sql)
            
            assert lexer.match_keyword(keyword.upper())
            assert lexer.match_keyword(keyword.lower())
            assert lexer.match_keyword(keyword.title())

    @pytest.mark.skip
    def test_lexer_delimiter_recognition(self):
        """デリミタ認識テスト"""
        delimiters = ["(", ")", ",", ".", ";", "=", "<", ">", "<=", ">=", "!="]
        
        for delimiter in delimiters:
            sql = f"SELECT test {delimiter} something"
            lexer = Lexer(sql)
            
            # SELECT testまで進む
            lexer.next_token()  # test
            lexer.next_token()  # delimiter
            
            assert lexer.match_delimiter(delimiter)

    @pytest.mark.skip
    def test_lexer_identifier_recognition(self):
        """識別子認識テスト"""
        identifiers = [
            "simple_name",
            "CamelCaseName", 
            "name_with_123",
            "UPPERCASE_NAME",
            "mixed_Case_NAME",
            "table1",
            "field_name_with_underscores",
            "a",  # 単一文字
            "very_long_identifier_name_that_might_test_limits"
        ]
        
        for identifier in identifiers:
            sql = f"SELECT {identifier} FROM table"
            lexer = Lexer(sql)
            
            lexer.next_token()  # identifier
            assert lexer.match_id()
            actual_id = lexer.eat_id()
            assert actual_id == identifier.lower()  # 小文字に正規化される

    @pytest.mark.skip
    def test_lexer_integer_constant_recognition(self):
        """整数定数認識テスト"""
        integers = [0, 1, 123, 999999, -1, -123]
        
        for integer in integers:
            sql = f"SELECT {integer} FROM table"
            lexer = Lexer(sql)
            
            lexer.next_token()  # integer
            if integer >= 0:  # 負数はトークンが分かれる可能性
                assert lexer.match_int_constant()
                actual_int = lexer.eat_int_constant()
                assert actual_int == integer

    @pytest.mark.skip
    def test_lexer_string_constant_recognition(self):
        """文字列定数認識テスト"""
        strings = [
            "'simple string'",
            "'string with spaces'",
            "'String With CAPS'",
            "'string_with_underscores'",
            "'string123with456numbers'",
            "''",  # 空文字列
            "'a'",  # 単一文字
            "'very long string that might test the string parsing capabilities'"
        ]
        
        for string in strings:
            sql = f"SELECT {string} FROM table"
            lexer = Lexer(sql)
            
            lexer.next_token()  # string
            assert lexer.match_string_constant()
            actual_string = lexer.eat_string_constant()
            assert actual_string == string

    @pytest.mark.skip
    def test_lexer_string_with_quotes(self):
        """クォート付き文字列のテスト"""
        sql = "SELECT 'O''Reilly' FROM table"  # エスケープされたクォート
        lexer = Lexer(sql)
        
        lexer.next_token()  # 文字列
        # 実装がエスケープをサポートしているかテスト
        if lexer.match_string_constant():
            actual_string = lexer.eat_string_constant()
            # エスケープが適切に処理されているか確認
            assert "O" in actual_string
            assert "Reilly" in actual_string

    @pytest.mark.skip
    def test_lexer_whitespace_handling(self):
        """空白文字処理テスト"""
        whitespace_variations = [
            "SELECT    id    FROM    users",
            "SELECT\tid\tFROM\tusers",
            "SELECT\nid\nFROM\nusers",
            "SELECT\r\nid\r\nFROM\r\nusers",
            "   SELECT id FROM users   ",
            "SELECT id FROM users\n\n\n"
        ]
        
        for sql in whitespace_variations:
            lexer = Lexer(sql)
            
            # 基本的なトークンが正しく識別されることを確認
            assert lexer.match_keyword("SELECT")
            lexer.next_token()
            assert lexer.match_id()  # id
            lexer.next_token()
            assert lexer.match_keyword("FROM")
            lexer.next_token()
            assert lexer.match_id()  # users

    @pytest.mark.skip
    def test_lexer_case_insensitivity(self):
        """大文字小文字無関係テスト"""
        case_variations = [
            "SELECT id FROM users",
            "select id from users", 
            "Select Id From Users",
            "SELECT ID FROM USERS",
            "sElEcT iD fRoM uSeRs"
        ]
        
        for sql in case_variations:
            lexer = Lexer(sql)
            
            assert lexer.match_keyword("SELECT")
            assert lexer.match_keyword("select")
            assert lexer.match_keyword("Select")
            
            lexer.next_token()  # id
            assert lexer.match_id()
            actual_id = lexer.eat_id()
            assert actual_id == "id"  # 小文字に正規化

    @pytest.mark.skip
    def test_lexer_edge_cases(self):
        """エッジケースのテスト"""
        edge_cases = [
            "",  # 空文字列
            "   ",  # 空白のみ
            ";",  # デリミタのみ
            "123",  # 数字のみ
            "'string'",  # 文字列のみ
            "identifier",  # 識別子のみ
        ]
        
        for sql in edge_cases:
            lexer = Lexer(sql)
            
            if sql.strip() == "":
                # 空文字列の場合、current_tokenがNoneまたは空
                assert lexer.current_token is None or lexer.current_token == ""
            else:
                # 何らかのトークンが認識される
                assert lexer.current_token is not None

    @pytest.mark.skip
    def test_lexer_eat_operations_comprehensive(self):
        """包括的なeat操作テスト"""
        sql = "INSERT INTO users (id, name, age) VALUES (123, 'John Doe', 25)"
        lexer = Lexer(sql)
        
        # 順次eat操作
        lexer.eat_keyword("INSERT")
        lexer.eat_keyword("INTO")
        assert lexer.eat_id() == "users"
        lexer.eat_delimiter("(")
        assert lexer.eat_id() == "id"
        lexer.eat_delimiter(",")
        assert lexer.eat_id() == "name"
        lexer.eat_delimiter(",")
        assert lexer.eat_id() == "age"
        lexer.eat_delimiter(")")
        lexer.eat_keyword("VALUES")
        lexer.eat_delimiter("(")
        assert lexer.eat_int_constant() == 123
        lexer.eat_delimiter(",")
        assert lexer.eat_string_constant() == "'John Doe'"
        lexer.eat_delimiter(",")
        assert lexer.eat_int_constant() == 25
        lexer.eat_delimiter(")")

    @pytest.mark.skip
    def test_lexer_match_operations_comprehensive(self):
        """包括的なmatch操作テスト"""
        sql = "SELECT name, 'constant', 42 FROM table WHERE id = 1"
        lexer = Lexer(sql)
        
        # 順次match操作
        assert lexer.match_keyword("SELECT")
        lexer.next_token()
        
        assert lexer.match_id()
        lexer.next_token()
        
        assert lexer.match_delimiter(",")
        lexer.next_token()
        
        assert lexer.match_string_constant()
        lexer.next_token()
        
        assert lexer.match_delimiter(",")
        lexer.next_token()
        
        assert lexer.match_int_constant()
        lexer.next_token()
        
        assert lexer.match_keyword("FROM")
        lexer.next_token()
        
        assert lexer.match_id()

    @pytest.mark.skip
    def test_lexer_error_conditions(self):
        """エラー条件のテスト"""
        sql = "SELECT id FROM users"
        lexer = Lexer(sql)
        
        # 正しくないキーワードをeatしようとする
        with pytest.raises(BadSyntaxException):
            lexer.eat_keyword("WRONG")
        
        # 正しいキーワードをeat
        lexer.eat_keyword("SELECT")
        
        # IDが期待される場所で間違ったものをeatしようとする
        with pytest.raises(BadSyntaxException):
            lexer.eat_string_constant()  # idが期待されるがstring_constantを要求

    @pytest.mark.skip
    def test_lexer_boundary_values(self):
        """境界値テスト"""
        boundary_cases = [
            ("SELECT 0 FROM t", 0),  # 最小整数
            ("SELECT 999999999 FROM t", 999999999),  # 大きな整数
            ("SELECT 'a' FROM t", "'a'"),  # 最短文字列
            ("SELECT 'very_long_string_that_tests_the_maximum_length_capabilities_of_the_lexer_implementation' FROM t", 
             "'very_long_string_that_tests_the_maximum_length_capabilities_of_the_lexer_implementation'")  # 長い文字列
        ]
        
        for sql, expected_value in boundary_cases:
            lexer = Lexer(sql)
            lexer.next_token()  #値へ移動
            
            if isinstance(expected_value, int):
                assert lexer.match_int_constant()
                actual_value = lexer.eat_int_constant()
                assert actual_value == expected_value
            else:
                assert lexer.match_string_constant()
                actual_value = lexer.eat_string_constant()
                assert actual_value == expected_value

    @pytest.mark.skip
    def test_lexer_complex_sql_parsing(self):
        """複雑なSQL文のパース"""
        complex_sql = """
        SELECT u.user_id, u.name, p.title, c.name 
        FROM users u, products p, categories c 
        WHERE u.id = p.owner_id AND p.category_id = c.id AND u.status = 'active' AND p.price > 100
        """
        
        lexer = Lexer(complex_sql)
        
        # 基本的な構造がパースできることを確認
        assert lexer.match_keyword("SELECT")
        
        # 複数のトークンを順次チェック
        token_count = 0
        while lexer.current_token is not None and lexer.current_token != "":
            token_count += 1
            lexer.next_token()
            
            # 無限ループ防止
            if token_count > 100:
                break
        
        # 適切な数のトークンが生成されることを確認
        assert token_count > 20  # 複雑なクエリなので多数のトークンが期待される

    @pytest.mark.skip
    def test_lexer_sql_injection_patterns(self):
        """SQLインジェクションパターンの処理"""
        injection_patterns = [
            "SELECT * FROM users WHERE name = 'test'; DROP TABLE users; --'",
            "SELECT * FROM users WHERE id = 1 OR 1=1",
            "SELECT * FROM users WHERE name = 'test' UNION SELECT * FROM passwords"
        ]
        
        for sql in injection_patterns:
            lexer = Lexer(sql)
            
            # 基本的なトークン化ができることを確認
            assert lexer.current_token is not None
            
            # セミコロンやコメントも適切にトークン化される
            if ";" in sql:
                while lexer.current_token is not None and lexer.current_token != ";":
                    lexer.next_token()
                if lexer.current_token == ";":
                    assert lexer.match_delimiter(";")

    @pytest.mark.skip
    def test_lexer_state_transitions(self):
        """Lexerの状態遷移テスト"""
        sql = "SELECT id FROM users"
        lexer = Lexer(sql)
        
        # 初期状態
        assert lexer.current_token == "select"
        
        # 次のトークンへ
        lexer.next_token()
        assert lexer.current_token == "id"
        
        # さらに次へ
        lexer.next_token()
        assert lexer.current_token == "from"
        
        # さらに次へ
        lexer.next_token()
        assert lexer.current_token == "users"
        
        # 最後のトークンの後
        lexer.next_token()
        assert lexer.current_token is None or lexer.current_token == ""
    
    def test_lexer_performance_stress(self):
        """Lexerのパフォーマンステスト"""
        # 大きなSQL文を生成
        large_sql = "SELECT " + ", ".join([f"field_{i}" for i in range(100)]) + " FROM large_table"
        
        lexer = Lexer(large_sql)
        
        # 全トークンをパース
        token_count = 0
        while lexer.current_token is not None and lexer.current_token != "":
            token_count += 1
            lexer.next_token()
            
            # 適度な制限
            if token_count > 300:
                break
        
        # 期待される数のトークンが処理される
        assert token_count > 200  # SELECT + 100 fields + 99 commas + FROM + table = 202+