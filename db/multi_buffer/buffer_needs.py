import math

from db.constants import Buffers


class BufferNeeds:

    @staticmethod
    def best_root(available: int, size: int) -> int:

        avail = available - Buffers.Reserved

        if avail <= Buffers.Minimum:
            return Buffers.Minimum

        k = float("inf")
        i = 1.0
        while k > avail:
            i += 1
            k = math.ceil(size ** (1 / i))

        return int(k)

    @staticmethod
    def best_factor(available: int, size: int) -> int:

        avail = available - Buffers.Reserved

        if avail <= Buffers.Minimum:
            return Buffers.Minimum

        k = float("inf")
        i = 1.0
        while k > avail:
            i += 1
            k = math.ceil(size / i)

        return int(k)
