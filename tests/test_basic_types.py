"""Test basic types validation."""

from __future__ import unicode_literals

import sys

import pytest

from object_validator import Bool, Integer, Float, String
from object_validator import InvalidTypeError, InvalidValueError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_bool():
    _validate(True, Bool())


def test_bool_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate(0, Bool())
    ).value

    assert error.object_name == ""
    assert error.object_type == int



def test_integer_int():
    _validate(1, Integer())


if PY2:
    def test_integer_long():
        _validate(long(1), Integer())


def test_integer_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate(True, Integer())
    ).value

    assert error.object_name == ""
    assert error.object_type == bool


def test_integer_min_max_valid():
    _validate(5, Integer(min=5, max=5))


def test_integer_min_invalid():
    with pytest.raises(InvalidValueError):
        _validate(5, Integer(min=6))


def test_integer_max_invalid():
    with pytest.raises(InvalidValueError):
        _validate(5, Integer(max=4))



def test_float():
    _validate(0.1, Float())


def test_float_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate(1, Float())
    ).value

    assert error.object_name == ""
    assert error.object_type == int



def test_string():
    _validate("string", String())


def test_string_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate(b"bytes", String())
    ).value

    assert error.object_name == ""
    assert error.object_type == bytes



def test_choices():
    _validate("b", String(choices=("a", "b")))


def test_choices_invalid_value():
    error = pytest.raises(InvalidValueError, lambda:
        _validate("c", String(choices=("a", "b")))
    ).value

    assert error.object_name == ""
    assert error.object_value == "c"



def _validate(obj, scheme):
    obj_copy = obj

    try:
        validated = scheme.validate(obj)
    finally:
        assert obj == obj_copy

    assert validated is obj
