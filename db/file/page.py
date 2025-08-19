import codecs
import struct
from typing import Optional

from db.constants import ByteSize, Format


class Page:

    CHARSET = "ascii"

    def __init__(self, block_size: int | bytes | bytearray):
        if isinstance(block_size, int):
            self.buffer = bytearray(block_size)
        elif isinstance(block_size, (bytes, bytearray)):
            self.buffer = bytearray(block_size)
        else:

            raise TypeError("block_size must be an int, bytes, or bytearray")

    def get_int(self, offset: int) -> int:
        """指定されたオフセットから4バイトの整数を取得"""

        result: int = struct.unpack_from(Format.IntLittleEndian, self.buffer, offset)[0]

        return result

    def set_int(self, offset: int, value: int) -> None:
        """指定されたオフセットに4バイトの整数を書き込む"""
        struct.pack_into(Format.IntLittleEndian, self.buffer, offset, value)

    def get_bytes(self, offset: int) -> bytes:
        """指定されたオフセットからバイト列を取得"""
        length = self.get_int(offset)
        start = offset + ByteSize.Int
        end = start + length
        return bytes(self.buffer[start:end])

    def set_bytes(self, offset: int, byte_data: bytes) -> None:
        """指定されたオフセットにバイト列を書き込む"""
        self.set_int(offset, len(byte_data))
        start = offset + ByteSize.Int
        self.buffer[start : start + len(byte_data)] = byte_data

    def get_string(self, offset: int) -> str:
        """指定されたオフセットから文字列を取得"""
        byte_string = self.get_bytes(offset)
        return byte_string.decode(self.CHARSET)

    def set_string(self, offset: int, value: str, max_length: Optional[int] = None) -> None:
        """指定されたオフセットに文字列を書き込む"""
        byte_string = value.encode(self.CHARSET)

        if max_length is not None and len(byte_string) > max_length:
            raise ValueError(f"String too long to store: actual={len(byte_string)} > max={max_length}")

        self.set_bytes(offset, byte_string)

    @staticmethod
    def get_max_length(string_length: int) -> int:
        bytes_per_char = len(codecs.lookup(Page.CHARSET).incrementalencoder().encode("a"))
        return ByteSize.Int + (string_length * bytes_per_char)

    def get_contents(self) -> bytes:
        """バッファ全体を含むバイト列を取得"""
        return bytes(self.buffer)
