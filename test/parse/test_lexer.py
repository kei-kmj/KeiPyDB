from db.parse.lexer import Lexer


def test_tokenize_distance_operator():
    lexer = Lexer("embedding <-> '[1.0, 2.0, 3.0]'")

    assert lexer.current_token == "embedding"
    lexer.next_token()
    assert lexer.current_token == "<->"
    lexer.next_token()
    assert lexer.current_token == "'[1.0, 2.0, 3.0]'"
