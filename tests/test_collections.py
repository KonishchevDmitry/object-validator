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


def test_list_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        List(Bool()).validate("list", tuple())
    ).value

    assert error.object_name == "list"
    assert error.object_type == tuple


def test_list_invalid_element_type():
    error = pytest.raises(InvalidTypeError, lambda:
        List(Bool()).validate("list", [False, 10, True])
    ).value

    assert error.object_name == "list[1]"
    assert error.object_type == int



def test_abstract_dict_default():
    AbstractDict().validate("obj", {
        True: 1,
        0: False,
        3.3: "float",
        "string": "string",
    })


def test_abstract_dict_key_value():
    AbstractDict(String(), Float()).validate("obj", {
        "one": 1.0,
        "two": 2.0,
    })


def test_abstract_dict_invalid_key_type():
    error = pytest.raises(InvalidTypeError, lambda:
        AbstractDict(key_type=String()).validate("dict", {
            True: "boolean",
            "string": "a",
        })
    ).value

    assert error.object_name == "dict[True]"
    assert error.object_type == bool


def test_abstract_dict_invalid_value_type():
    error = pytest.raises(InvalidTypeError, lambda:
        AbstractDict(value_type=String()).validate("dict", {
            False: 0,
            "string": "a",
        })
    ).value

    assert error.object_name == "dict[False]"
    assert error.object_type == int



def test_dict_empty():
    Dict({}).validate("obj", {})


def test_dict_with_schema():
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


def test_dict_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        Dict({}).validate("dict", object())
    ).value

    assert error.object_name == "dict"
    assert error.object_type == object


def test_dict_unknown_parameter():
    assert pytest.raises(UnknownParameterError, lambda:
        Dict({1: Bool()}).validate("dict", {
            1: True,
            False: "value",
        })
    ).value.object_name == "dict[False]"


def test_dict_missing_parameter():
    assert pytest.raises(MissingParameterError, lambda:
        Dict({1: Bool(), 2: String()}).validate("dict", {
            2: "value",
        })
    ).value.object_name == "dict[1]"
