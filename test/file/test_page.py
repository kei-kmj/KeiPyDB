import pytest

from db.constants import ByteSize
from db.file.page import Page


def test_new_page():
    block_size = 4096
    page = Page(block_size)

    assert page is not None
    assert page.buffer == bytearray(block_size)
    assert len(page.get_contents()) == block_size
    assert page.CHARSET == "ascii"


def test_new_page_various_sizes():
    sizes = [128, 512, 1024, 4096, 8192]
    
    for size in sizes:
        page = Page(size)
        assert len(page.buffer) == size
        assert len(page.get_contents()) == size
        # 初期化時はすべて0
        assert all(b == 0 for b in page.buffer)


def test_new_page_from_bytes():
    block_size = 4096
    data = bytearray(block_size)
    page = Page(data)

    assert page is not None
    assert len(page.get_contents()) == block_size
    assert page.CHARSET == "ascii"
    
    # bytesからの初期化もテスト
    byte_data = bytes(block_size)
    page2 = Page(byte_data)
    assert len(page2.get_contents()) == block_size


def test_new_page_invalid_type():
    with pytest.raises(TypeError):
        Page("invalid")
    
    with pytest.raises(TypeError):
        Page(3.14)
    
    with pytest.raises(TypeError):
        Page([1, 2, 3])


def test_page_int():
    page = Page(4096)
    offset = 0
    value = 42
    page.set_int(offset, value)
    assert page.get_int(offset) == value


def test_page_int_various_values():
    page = Page(4096)
    
    test_values = [
        (0, 0),
        (0, 1),
        (0, -1),
        (0, 2147483647),  # Max 32-bit int
        (0, -2147483648),  # Min 32-bit int
        (100, 12345),
        (200, -67890),
    ]
    
    for offset, value in test_values:
        page.set_int(offset, value)
        assert page.get_int(offset) == value


def test_page_int_multiple_values():
    page = Page(4096)
    
    # 複数の整数を異なる位置に書き込み
    values = [(0, 100), (4, 200), (8, 300), (12, 400)]
    
    for offset, value in values:
        page.set_int(offset, value)
    
    # すべての値が正しく読み取れることを確認
    for offset, expected in values:
        assert page.get_int(offset) == expected


def test_page_bytes():
    page = Page(4096)
    offset = 0
    value = b"hello"
    page.set_bytes(offset, value)
    assert page.get_bytes(offset) == value


def test_page_bytes_various_data():
    page = Page(4096)
    
    test_cases = [
        (0, b""),  # 空のバイト列
        (100, b"hello world"),
        (200, b"\x00\x01\x02\x03"),  # バイナリデータ
        (300, b"a" * 100),  # 長いデータ
        (500, bytes(range(256))),  # すべてのバイト値
    ]
    
    for offset, data in test_cases:
        page.set_bytes(offset, data)
        assert page.get_bytes(offset) == data


def test_page_string():
    page = Page(4096)
    offset = 0
    value = "hello"
    page.set_string(offset, value)
    assert page.get_string(offset) == value


def test_page_string_various_data():
    page = Page(4096)
    
    test_cases = [
        (0, ""),  # 空文字列
        (100, "Hello, World!"),
        (200, "123456789"),
        (300, "Special chars: !@#$%^&*()"),
        (400, "a" * 50),  # 長い文字列
    ]
    
    for offset, text in test_cases:
        page.set_string(offset, text)
        assert page.get_string(offset) == text


def test_page_string_with_max_length():
    page = Page(4096)
    offset = 0
    
    # 最大長以内の文字列
    page.set_string(offset, "hello", max_length=10)
    assert page.get_string(offset) == "hello"
    
    # 最大長を超える文字列
    with pytest.raises(ValueError) as exc_info:
        page.set_string(offset, "a" * 20, max_length=10)
    assert "String too long to store" in str(exc_info.value)


def test_page_mixed_data():
    page = Page(4096)
    
    # 異なる型のデータを異なる位置に書き込み
    page.set_int(0, 42)
    page.set_string(4, "test string")
    page.set_bytes(100, b"binary data")
    page.set_int(200, -999)
    
    # すべて正しく読み取れることを確認
    assert page.get_int(0) == 42
    assert page.get_string(4) == "test string"
    assert page.get_bytes(100) == b"binary data"
    assert page.get_int(200) == -999


def test_page_max_length():
    string_length = 1024
    assert Page.get_max_length(string_length) == 4 + (string_length * 1)
    
    # 異なる長さでテスト
    assert Page.get_max_length(0) == ByteSize.Int
    assert Page.get_max_length(100) == ByteSize.Int + 100
    assert Page.get_max_length(1) == ByteSize.Int + 1


def test_page_get_contents():
    size = 256
    page = Page(size)
    
    # 初期状態
    contents = page.get_contents()
    assert len(contents) == size
    assert all(b == 0 for b in contents)
    
    # contentsとpage.bufferは同じオブジェクトを参照している
    assert contents is page.buffer
    
    # データを書き込んだ後
    page.set_int(0, 12345)
    page.set_string(10, "test")
    
    contents2 = page.get_contents()
    assert len(contents2) == size
    
    # contentsとcontents2は同じオブジェクト（page.buffer）を参照しているため、
    # 内容は同じになる
    assert contents2 is contents
    assert contents2 is page.buffer
    
    # ただし、内容自体は変更されている
    assert page.get_int(0) == 12345
    assert page.get_string(10) == "test"
