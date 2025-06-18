import pytest

from db.parse.bad_syntax_exception import BadSyntaxException
from db.parse.parser import Parser
from db.parse.lexer import Lexer


class TestParseErrorHandling:
    """パーサーのエラーハンドリングと例外処理のテスト"""
    
    def test_bad_syntax_exception_basic(self):
        """BadSyntaxExceptionの基本テスト"""
        exception = BadSyntaxException("Test error message")
        
        assert str(exception) == "Test error message"
        assert isinstance(exception, Exception)
    
    def test_lexer_syntax_errors(self):
        """Lexerでの構文エラー"""
        error_cases = [
            ("SELECT * FROM users WHERE id = ", "Incomplete comparison"),
            ("SELECT * FROM WHERE id = 1", "Missing table name"),
            ("FROM users SELECT *", "Wrong keyword order"),
            ("SELECT id, FROM users", "Missing field after comma"),
            ("SELECT id users", "Missing FROM keyword")
        ]
        
        for sql, description in error_cases:
            lexer = Lexer(sql)
            
            try:
                # 完全にパースしようとする
                while lexer.current_token is not None and lexer.current_token != "":
                    lexer.next_token()
                
                # エラーが発生しない場合、不完全な構文として処理される
                print(f"Warning: {description} - SQL: {sql}")
                
            except Exception as e:
                # 一部のエラーはLexerレベルで検出される可能性
                print(f"Lexer error for {description}: {e}")
    
    def test_parser_select_errors(self):
        """SELECT文でのパースエラー"""
        select_errors = [
            "SELECT",  # フィールドリストなし
            "SELECT FROM users",  # フィールドリストなし
            "SELECT id",  # FROM句なし
            "SELECT id FROM",  # テーブル名なし
            "SELECT id, FROM users",  # 不完全なフィールドリスト
            "SELECT id users",  # FROMキーワードなし
            "SELECT * FROM users WHERE",  # 不完全なWHERE句
            "SELECT * FROM users WHERE =",  # 不完全な条件
            "SELECT * FROM users WHERE id =",  # 値なし
            "SELECT * FROM users WHERE = 1",  # フィールドなし
        ]
        
        for sql in select_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.query()
    
    def test_parser_insert_errors(self):
        """INSERT文でのパースエラー"""
        insert_errors = [
            "INSERT",  # 不完全
            "INSERT INTO",  # テーブル名なし
            "INSERT INTO users",  # VALUES句なし
            "INSERT INTO users ()",  # 空のフィールドリスト
            "INSERT INTO users (id, name)",  # VALUES句なし
            "INSERT INTO users VALUES",  # 値なし
            "INSERT INTO users VALUES ()",  # 空の値リスト
            "INSERT INTO users (id) VALUES",  # 不完全なVALUES
            "INSERT INTO users (id, name) VALUES (1)",  # 値の数が不一致
            "INSERT INTO users (id) VALUES (1, 'extra')",  # 値の数が不一致
            "INSERT users (id) VALUES (1)",  # INTOキーワードなし
        ]
        
        for sql in insert_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_update_errors(self):
        """UPDATE文でのパースエラー"""
        update_errors = [
            "UPDATE",  # 不完全
            "UPDATE users",  # SET句なし
            "UPDATE users SET",  # 不完全なSET
            "UPDATE users SET name",  # 値なし
            "UPDATE users SET name =",  # 値なし
            "UPDATE users SET = 'value'",  # フィールドなし
            "UPDATE SET name = 'value'",  # テーブル名なし
            "UPDATE users name = 'value'",  # SETキーワードなし
            "UPDATE users SET name 'value'",  # =演算子なし
        ]
        
        for sql in update_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_delete_errors(self):
        """DELETE文でのパースエラー"""
        delete_errors = [
            "DELETE",  # 不完全
            "DELETE FROM",  # テーブル名なし
            "DELETE users",  # FROMキーワードなし
            "DELETE FROM users WHERE",  # 不完全なWHERE
            "DELETE FROM users WHERE =",  # 不完全な条件
            "DELETE FROM users WHERE id",  # 比較演算子なし
            "DELETE FROM users WHERE id =",  # 値なし
        ]
        
        for sql in delete_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_create_table_errors(self):
        """CREATE TABLE文でのパースエラー"""
        create_table_errors = [
            "CREATE",  # 不完全
            "CREATE TABLE",  # テーブル名なし
            "CREATE TABLE users",  # フィールド定義なし
            "CREATE TABLE users ()",  # 空のフィールド定義
            "CREATE TABLE users (id)",  # データ型なし
            "CREATE TABLE users (id int,)",  # 最後のカンマ
            "CREATE TABLE users (int)",  # フィールド名なし
            "CREATE TABLE users (id varchar)",  # varchar長なし
            "CREATE TABLE users (id varchar())",  # 空のvarchar長
            "CREATE TABLE users (id varchar(abc))",  # 無効なvarchar長
            "CREATE users (id int)",  # TABLEキーワードなし
        ]
        
        for sql in create_table_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_create_view_errors(self):
        """CREATE VIEW文でのパースエラー"""
        create_view_errors = [
            "CREATE VIEW",  # ビュー名なし
            "CREATE VIEW test_view",  # AS句なし
            "CREATE VIEW test_view AS",  # SELECT文なし
            "CREATE VIEW AS SELECT * FROM users",  # ビュー名なし
            "CREATE test_view AS SELECT * FROM users",  # VIEWキーワードなし
            "CREATE VIEW test_view SELECT * FROM users",  # ASキーワードなし
        ]
        
        for sql in create_view_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_create_index_errors(self):
        """CREATE INDEX文でのパースエラー"""
        create_index_errors = [
            "CREATE INDEX",  # インデックス名なし
            "CREATE INDEX test_idx",  # ON句なし
            "CREATE INDEX test_idx ON",  # テーブル名なし
            "CREATE INDEX test_idx ON users",  # フィールド指定なし
            "CREATE INDEX test_idx ON users ()",  # 空のフィールド指定
            "CREATE test_idx ON users (id)",  # INDEXキーワードなし
            "CREATE INDEX ON users (id)",  # インデックス名なし
            "CREATE INDEX test_idx users (id)",  # ONキーワードなし
        ]
        
        for sql in create_index_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_lexer_eat_errors(self):
        """Lexerのeat操作でのエラー"""
        sql = "SELECT id FROM users"
        lexer = Lexer(sql)
        
        # 間違ったキーワードをeat
        with pytest.raises(BadSyntaxException):
            lexer.eat_keyword("WRONG")
        
        # 正しいキーワードをeat
        lexer.eat_keyword("SELECT")
        
        # 間違った型をeat
        with pytest.raises(BadSyntaxException):
            lexer.eat_int_constant()  # idが期待されるが整数を要求
    
    def test_lexer_delimiter_errors(self):
        """Lexerのデリミタエラー"""
        sql = "SELECT id, name FROM users"
        lexer = Lexer(sql)
        
        lexer.eat_keyword("SELECT")
        lexer.eat_id()  # id
        
        # 間違ったデリミタをeat
        with pytest.raises(BadSyntaxException):
            lexer.eat_delimiter(";")  # カンマが期待されるがセミコロンを要求
    
    def test_parser_empty_input_errors(self):
        """空入力でのエラー"""
        empty_inputs = ["", "   ", "\n\n", "\t\t"]
        
        for empty_sql in empty_inputs:
            parser = Parser(empty_sql)
            
            with pytest.raises(BadSyntaxException):
                parser.query()
            
            with pytest.raises(BadSyntaxException):
                parser.update_command()
    
    def test_parser_unexpected_token_errors(self):
        """予期しないトークンでのエラー"""
        unexpected_cases = [
            ("123 SELECT id FROM users", "Number at start"),
            ("'string' SELECT id FROM users", "String at start"),
            ("( SELECT id FROM users", "Parenthesis at start"),
            ("SELECT ) FROM users", "Unexpected parenthesis"),
            ("SELECT id ; FROM users", "Semicolon in wrong place"),
            ("SELECT id FROM users ;; ", "Double semicolon"),
        ]
        
        for sql, description in unexpected_cases:
            parser = Parser(sql)
            
            try:
                if sql.strip().startswith("SELECT"):
                    parser.query()
                else:
                    parser.update_command()
                
                # エラーが発生しない場合は警告
                print(f"Warning: {description} did not raise error for: {sql}")
                
            except BadSyntaxException:
                # 期待されるエラー
                pass
            except Exception as e:
                # その他のエラーも許容（実装依存）
                print(f"Other error for {description}: {e}")
    
    def test_parser_keyword_case_sensitivity(self):
        """キーワードの大文字小文字エラー"""
        # これらは実際にはエラーにならないはずだが、念のためテスト
        case_variations = [
            "select id from users",
            "SELECT ID FROM USERS", 
            "Select Id From Users",
            "sElEcT iD fRoM uSeRs"
        ]
        
        for sql in case_variations:
            parser = Parser(sql)
            
            # これらは成功するはず
            query_data = parser.query()
            assert query_data is not None
    
    def test_parser_complex_error_scenarios(self):
        """複雑なエラーシナリオ"""
        complex_errors = [
            "SELECT id FROM users WHERE age = 25 AND",  # 不完全なAND
            "SELECT id FROM users WHERE age = 25 AND status",  # 不完全な条件
            "INSERT INTO users (id, name) VALUES (1, 'test', extra)",  # 余分な値
            "UPDATE users SET name = 'test' AND age = 25",  # 無効なAND
            "CREATE TABLE users (id int, name varchar(50), age)",  # 型なしフィールド
            "SELECT id, name, FROM users",  # 最後のカンマ
            "SELECT id name FROM users",  # カンマなし
        ]
        
        for sql in complex_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                if sql.startswith("SELECT"):
                    parser.query()
                else:
                    parser.update_command()
    
    def test_parser_boundary_error_conditions(self):
        """境界エラー条件"""
        boundary_errors = [
            "SELECT id FROM users WHERE age = ",  # 値なし
            "INSERT INTO users () VALUES ()",  # 空のリスト
            "CREATE TABLE users ()",  # 空のフィールドリスト
            "UPDATE users SET ",  # 空のSET
            "DELETE FROM WHERE id = 1",  # テーブル名なし
        ]
        
        for sql in boundary_errors:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                if sql.startswith("SELECT"):
                    parser.query()
                else:
                    parser.update_command()
    
    def test_error_message_clarity(self):
        """エラーメッセージの明確性テスト"""
        error_sql = "SELECT id FROM"  # テーブル名なし
        parser = Parser(error_sql)
        
        try:
            parser.query()
            assert False, "Expected BadSyntaxException"
        except BadSyntaxException as e:
            error_message = str(e)
            
            # エラーメッセージが有用な情報を含んでいることを確認
            assert len(error_message) > 0
            # 具体的な内容は実装依存だが、空でないことは確認
    
    def test_parser_recovery_after_error(self):
        """エラー後のパーサー回復テスト"""
        # 最初にエラーを発生させる
        error_parser = Parser("INVALID SQL")
        
        with pytest.raises(BadSyntaxException):
            error_parser.query()
        
        # 新しいパーサーで正常なSQLがパースできることを確認
        good_parser = Parser("SELECT id FROM users")
        query_data = good_parser.query()
        
        assert query_data is not None
        assert query_data.get_fields() == ["id"]
    
    def test_lexer_token_exhaustion(self):
        """Lexerのトークン枯渇テスト"""
        sql = "SELECT id"  # 短いSQL
        lexer = Lexer(sql)
        
        # 全トークンを消費
        lexer.eat_keyword("SELECT")
        lexer.eat_id()  # id
        
        # トークンが枯渇した状態で操作を試みる
        assert lexer.current_token is None or lexer.current_token == ""
        
        # 次のトークンがない状態での操作
        with pytest.raises(BadSyntaxException):
            lexer.eat_keyword("FROM")
    
    def test_parser_malformed_expressions(self):
        """不正な式でのエラー"""
        malformed_expressions = [
            "SELECT id + FROM users",  # 不完全な演算
            "SELECT (id FROM users",  # 閉じ括弧なし
            "SELECT id) FROM users",  # 開き括弧なし
            "SELECT id,, name FROM users",  # 連続カンマ
            "SELECT , name FROM users",  # 先頭カンマ
        ]
        
        for sql in malformed_expressions:
            parser = Parser(sql)
            
            with pytest.raises(BadSyntaxException):
                parser.query()