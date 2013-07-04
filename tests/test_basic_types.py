"""Test basic types validation."""

from __future__ import unicode_literals

import sys

import pytest

from json_validator import Bool, Integer, Float, String
from json_validator import InvalidTypeError, InvalidValueError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_bool():
    Bool().validate("obj", True)
    Bool().validate("obj", False)


def test_bool_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        Bool().validate("invalid", 0)
    ).value

    assert error.object_name == "invalid"
    assert error.object_type == int



def test_integer():
    Integer().validate("obj", 1)

    if PY2:
        Integer().validate("obj", long(1))


def test_integer_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        Integer().validate("invalid", True)
    ).value

    assert error.object_name == "invalid"
    assert error.object_type == bool



def test_float():
    Float().validate("obj", 0.1)


def test_float_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        Float().validate("invalid", 1)
    ).value

    assert error.object_name == "invalid"
    assert error.object_type == int



def test_string():
    String().validate("obj", "string")


def test_string_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        String().validate("invalid", b"bytes")
    ).value

    assert error.object_name == "invalid"
    assert error.object_type == bytes



def test_choices():
    String(choices=("a", "b")).validate("obj", "b")


def test_choices_invalid_value():
    error = pytest.raises(InvalidValueError, lambda:
        String(choices=("a", "b")).validate("invalid", "c")
    ).value

    assert error.object_name == "invalid"
    assert error.object_value == "c"
