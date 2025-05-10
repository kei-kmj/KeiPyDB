from db.file.page import Page


def test_new_page():
    block_size = 4096
    page = Page(block_size)

    assert page is not None
    assert page.buffer == bytearray(block_size)
    assert len(page.get_contents()) == block_size
    assert page.CHARSET == "ascii"


def test_new_page_from_bytes():
    block_size = 4096
    data = bytearray(block_size)
    page = Page(data)

    assert page is not None
    assert len(page.get_contents()) == block_size
    assert page.CHARSET == "ascii"


def test_page_int():
    page = Page(4096)
    offset = 0
    value = 42
    page.set_int(offset, value)
    assert page.get_int(offset) == value


def test_page_bytes():
    page = Page(4096)
    offset = 0
    value = b"hello"
    page.set_bytes(offset, value)
    assert page.get_bytes(offset) == value


def test_page_string():
    page = Page(4096)
    offset = 0
    value = "hello"
    page.set_string(offset, value)
    assert page.get_string(offset) == value


def test_page_max_length():
    string_length = 1024
    assert Page.get_max_length(string_length) == 4 + (string_length * 1)
