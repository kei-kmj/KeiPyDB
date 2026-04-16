import math

type Vector = list[float]


def cosine_distance(u: list[float], v: list[float]) -> float:
    """コサイン距離を計算する関数"""
    dot_product = sum(x * y for x, y in zip(u, v))
    norm_u = math.sqrt(sum(x**2 for x in u))
    norm_v = math.sqrt(sum(y**2 for y in v))

    return 1 - (dot_product / (norm_u * norm_v))


def parse_vector_literal(vector_literal: str) -> list[float]:
    vector_literal = vector_literal.strip()
    if not (vector_literal.startswith("[") and vector_literal.endswith("]")):
        raise SyntaxError(f"Expected vector literal in the form of [v1, v2, ...], but found {vector_literal}")
    return [float(v.strip()) for v in vector_literal[1:-1].split(",")]
