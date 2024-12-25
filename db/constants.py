class Format:
    IntBigEndian = ">i"


class ByteSize:
    Int = 4


class FileModes:
    Read = "rb"
    Write = "wb"
    ReadWrite = "r+b"
    WriteNew = "w+b"


class LogRecordFields:
    ONE_FIELD = 1
    TWO_FIELDS = 2
