import pytest

from db.query.constant import Constant


def test_integer_constant_initialization():
    constant = Constant(1)
    assert constant.int_value == 1
    assert constant.as_int() == 1
    assert constant.is_int() is True


def test_string_constant_initialization():
    constant = Constant("test")
    assert constant.str_value == "test"
    assert constant.as_string() == "test"
    assert constant.is_int() is False


def test_constant_comprehensive():
    """Test Constant class thoroughly"""

    # Test integer constant
    int_const = Constant(42)
    assert int_const.as_int() == 42
    assert int_const.is_int() is True
    assert int_const.int_value == 42

    # Test string constant
    str_const = Constant("Hello")
    assert str_const.as_string() == "Hello"
    assert str_const.is_int() is False
    assert str_const.str_value == "Hello"

    # Test equality
    const1 = Constant(42)
    const2 = Constant(42)
    const3 = Constant(43)
    assert const1 == const2
    assert const1 != const3

    # Test comparison
    assert Constant(10) < Constant(20)
    assert Constant("apple") < Constant("banana")

    # Test hashing
    assert hash(const1) == hash(const2)
    const_set = {const1, const2}
    assert len(const_set) == 1
