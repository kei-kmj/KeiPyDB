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


class Slot:
    First = 0


NODE_DIVISOR = 2


class Node:
    OVERFLOW = -1
    VALID = 0
