import struct

from db.file.constants import ByteSize, Format
from db.file.page import Page


def test_整数の読み書きができる():
    page = Page(1024)
    page.set_int(0, 100)
    assert page.get_int(0) == 100


def test_バイト列の読み書きができる():
    page = Page(1024)
    data = b"Hello, world!"
    page.set_bytes(0, data)
    assert page.get_bytes(0) == data


def test_文字列の読み書きができる():
    page = Page(1024)
    data = "Hello, world!"
    page.set_string(0, data)
    assert page.get_string(0) == data


def test_文字列の最大長を取得できる():
    string_length = 10
    assert Page.get_max_length(string_length) == ByteSize.Int + string_length


def test_ページの内容を取得できる():
    page = Page(1024)
    page.set_int(0, 12345)
    page.set_string(10, "test")
    string_length = len("test")
    raw_content = page.get_contents()

    assert raw_content[:4] == struct.pack(Format.IntBigEndian, 12345)
    assert raw_content[10:10 + ByteSize.Int + string_length] == struct.pack(Format.IntBigEndian, string_length) + b"test"