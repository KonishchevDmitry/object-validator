"""Test collection types validation."""

from __future__ import unicode_literals

import sys

import pytest

from json_validator import Bool, Integer, Float, String, List, AbstractDict, Dict
from json_validator import InvalidTypeError, MissingParameterError, UnknownParameterError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_list():
    List(Bool()).validate("obj", [])
    List(Bool()).validate("obj", [True, False])

    assert pytest.raises(InvalidTypeError, lambda:
        List(Bool()).validate("list", tuple())
    ).value.object_name == "list"

    assert pytest.raises(InvalidTypeError, lambda:
        List(Bool()).validate("list", [False, 10, True])
    ).value.object_name == "list[1]"


def test_abstract_dict():
    AbstractDict().validate("obj", {
        True: 1,
        0: False,
        3.3: "float",
        "string": "string",
    })

    AbstractDict(String(), Float()).validate("obj", {
        "one": 1.0,
        "two": 2.0,
    })

    assert pytest.raises(InvalidTypeError, lambda:
        AbstractDict(key_type=String()).validate("dict", {
            True: "boolean",
            "string": "a",
        })
    ).value.object_name == "dict[True]"

    assert pytest.raises(InvalidTypeError, lambda:
        AbstractDict(value_type=String()).validate("dict", {
            False: 0,
            "string": "a",
        })
    ).value.object_name == "dict[False]"


def test_dict():
    Dict({}).validate("obj", {})

    Dict({
        False: String(),
        1: Bool(),
        "integer": Integer(),
        3.3: Float(optional=True),
    }).validate("obj", {
        False: "string",
        1: True,
        "integer": 10,
    })

    assert pytest.raises(InvalidTypeError, lambda:
        Dict({}).validate("dict", object())
    ).value.object_name == "dict"

    assert pytest.raises(UnknownParameterError, lambda:
        Dict({1: Bool()}).validate("dict", {
            1: True,
            False: "value",
        })
    ).value.object_name == "dict[False]"

    assert pytest.raises(MissingParameterError, lambda:
        Dict({1: Bool(), 2: String()}).validate("dict", {
            2: "value",
        })
    ).value.object_name == "dict[1]"
