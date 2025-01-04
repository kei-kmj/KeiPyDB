import codecs
import struct
from io import BytesIO

from db.constants import ByteSize, Format


class Page:

    CHARSET = "ascii"

    def __init__(self, block_size: int | bytes | bytearray):
        if isinstance(block_size, int):
            self.buffer = BytesIO(bytearray(block_size))
        elif isinstance(block_size, (bytes, bytearray)):
            self.buffer = BytesIO(block_size)
        else:
            raise TypeError("block_size must be an int, bytes, or bytearray")

    def get_int(self, offset: int) -> int:
        self.buffer.seek(offset)
        data = self.buffer.read(4)

        return 0 if not data else struct.unpack(Format.IntBigEndian, data)[0]

    def set_int(self, offset: int, value: int) -> None:
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(Format.IntBigEndian, value))

    def get_bytes(self, offset: int) -> bytes:

        self.buffer.seek(offset)
        length = struct.unpack(Format.IntBigEndian, self.buffer.read(4))[0]
        return self.buffer.read(length)

    def set_bytes(self, offset: int, byte_data: bytes) -> None:
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(">i", len(byte_data)))
        self.buffer.write(byte_data)

    def get_string(self, offset: int) -> str:
        return self.get_bytes(offset).decode(self.CHARSET)

    def set_string(self, offset: int, value: str) -> None:
        self.set_bytes(offset, value.encode(self.CHARSET))

    @staticmethod
    def get_max_length(string_length: int) -> int:
        bytes_per_char = len(codecs.lookup(Page.CHARSET).incrementalencoder().encode("a"))
        return ByteSize.Int + (string_length * bytes_per_char)

    def get_contents(self) -> BytesIO:
        self.buffer.seek(0)
        return self.buffer
