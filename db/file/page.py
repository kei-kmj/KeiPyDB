import struct
from io import BytesIO

from db.file.constants import ByteSize, Format


class Page:

    CHARSET = "ascii"

    def __init__(self, block_size: int | bytes | bytearray):

        if isinstance(block_size, int):
            self.buffer = BytesIO(bytearray(block_size))
        elif isinstance(block_size, (bytes, bytearray)):
            self.buffer = BytesIO(block_size)
        else:
            raise ValueError("block_size must be int or bytes")

    def get_int(self, offset: int) -> int:
        self.buffer.seek(offset)
        result: int = struct.unpack(Format.IntBigEndian, self.buffer.read(ByteSize.Int))[0]
        return result

    def set_int(self, offset: int, value: int) -> None:
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(Format.IntBigEndian, value))

    def get_bytes(self, offset: int) -> bytes:
        self.buffer.seek(offset)
        length = struct.unpack(Format.IntBigEndian, self.buffer.read(ByteSize.Int))[0]

        return self.buffer.read(length)

    def set_bytes(self, offset: int, byte_data: bytes) -> None:
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(Format.IntBigEndian, len(byte_data)))
        self.buffer.write(byte_data)

    def get_string(self, offset: int) -> str:
        byte_data = self.get_bytes(offset)
        return byte_data.decode(self.CHARSET)

    def set_string(self, offset: int, value: str) -> None:
        byte_data = value.encode(self.CHARSET)
        self.set_bytes(offset, byte_data)

    @staticmethod
    def get_max_length(string_length: int) -> int:
        return ByteSize.Int + string_length

    def get_contents(self) -> bytes:
        return self.buffer.getvalue()
