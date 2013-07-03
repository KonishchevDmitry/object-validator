"""Test basic types validation."""

from __future__ import unicode_literals

import sys

import pytest

from json_validator import Bool, Integer, Float, String, InvalidType

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_bool():
    Bool().validate("obj", True)
    Bool().validate("obj", False)

    assert pytest.raises(InvalidType, lambda:
        Bool().validate("invalid", 0)
    ).value.object_name == "invalid"


def test_integer():
    Integer().validate("obj", 1)

    if PY2:
        Integer().validate("obj", long(1))

    assert pytest.raises(InvalidType, lambda:
        Integer().validate("invalid", True)
    ).value.object_name == "invalid"


def test_float():
    Float().validate("obj", 0.1)

    assert pytest.raises(InvalidType, lambda:
        Float().validate("invalid", 1)
    ).value.object_name == "invalid"


def test_string():
    String().validate("obj", "string")

    assert pytest.raises(InvalidType, lambda:
        String().validate("invalid", b"bytes")
    ).value.object_name == "invalid"
