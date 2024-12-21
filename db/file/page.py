import struct
from io import BytesIO

from db.file.constants import ByteSize, Format


class Page:

    CHARSET = "ascii"

    def __init__(self, block_size):

        if isinstance(block_size, int) :
            self.buffer = BytesIO(bytearray(block_size))
        elif isinstance(block_size, (bytes, bytearray)):
            self.buffer = BytesIO(block_size)
        else:
            raise ValueError("block_size must be int or bytes")

    def get_int(self, offset):
        self.buffer.seek(offset)
        return struct.unpack(Format.IntBigEndian, self.buffer.read(ByteSize.Int))[0]


    def set_int(self, offset, value):
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(Format.IntBigEndian, value))


    def get_bytes(self, offset):
        self.buffer.seek(offset)
        length = struct.unpack(Format.IntBigEndian, self.buffer.read(ByteSize.Int))[0]

        return self.buffer.read(length)


    def set_bytes(self, offset, byte_data):
        self.buffer.seek(offset)
        self.buffer.write(struct.pack(Format.IntBigEndian, len(byte_data)))
        self.buffer.write(byte_data)


    def get_string(self, offset):
        byte_data = self.get_bytes(offset)
        return byte_data.decode(self.CHARSET)


    def set_string(self, offset, value):
        byte_data = value.encode(self.CHARSET)
        self.set_bytes(offset, byte_data)


    @staticmethod
    def get_max_length(string_length):
        return ByteSize.Int + string_length


    def get_contents(self):
        return self.buffer.getvalue()





