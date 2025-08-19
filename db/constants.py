class Format:
    IntBigEndian = ">i"
    IntLittleEndian = "<i"


class ByteSize:
    Int = 4
    ASCII = 1


class FileMode:
    Read = "rb"
    Write = "wb"
    ReadWrite = "r+b"
    WriteNew = "w+b"


class LogRecordFields:
    One_Field = 1
    Two_Fields = 2


class LockType:
    Shared = "S"
    Exclusive = "X"


class LockMode:
    No_Lock = 0
    Shared_Lock = 1
    Exclusive_Lock = -1


class FieldType:
    Integer = 1
    Varchar = 2


class SchemaType:
    Int = "int"
    Float = "float"


class Slot:
    First = 0


NODE_DIVISOR = 2
MAX_RUNS_FOR_MERGE = 2


class Node:
    Overflow = -1
    Valid = 0


class ListIndex:
    First = 0


class Buffers:
    Reserved = 2
    Minimum = 1
