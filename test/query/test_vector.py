import pytest

from db.query.vector import cosine_distance, parse_vector_literal


def test_cosine_distance_identical():

    vec1 = [0.1, 0.2, 0.3]
    vec2 = [0.1, 0.2, 0.3]

    distance = cosine_distance(vec1, vec2)
    assert distance == 0.0


def test_cosine_distance_orthogonal():

    vec1 = [0.1, 0.0, 0.0]
    vec2 = [0.0, 0.1, 0.0]

    distance = cosine_distance(vec1, vec2)
    assert distance == 1.0


def test_cosine_distance_opposite():

    vec1 = [0.1, 0.2, 0.3]
    vec2 = [-0.1, -0.2, -0.3]

    distance = cosine_distance(vec1, vec2)
    assert distance == 2.0


def test_parse_vector_literal():

    vector_literal = "[0.1, 0.2, 0.3]"
    expected_vector = [0.1, 0.2, 0.3]

    parsed_vector = parse_vector_literal(vector_literal)
    assert parsed_vector == expected_vector


def test_parse_vector_literal_invalid():

    with pytest.raises(SyntaxError):
        parse_vector_literal("1.0, 2.0, 3.0")
