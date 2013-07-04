"""Test collection types validation."""

from __future__ import unicode_literals

import copy
import sys

import pytest

from json_validator import Bool, Integer, Float, String, List, AbstractDict, Dict
from json_validator import InvalidTypeError, MissingParameterError, UnknownParameterError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_list_empty():
    _validate([], List(Bool()))


def test_list_full():
    _validate([True, False], List(Bool()))


def test_list_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate(tuple(), List(Bool()))
    ).value

    assert error.object_name == ""
    assert error.object_type == tuple


def test_list_invalid_element_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate([False, 10, True], List(Bool()))
    ).value

    assert error.object_name == "[1]"
    assert error.object_type == int



def test_abstract_dict_default():
    _validate({
        True: 1,
        0: False,
        3.3: "float",
        "string": "string",
    }, AbstractDict())


def test_abstract_dict_key_value():
    _validate({
        "one": 1.0,
        "two": 2.0,
    }, AbstractDict(String(), Float()))


def test_abstract_dict_invalid_key_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate({
            True: "boolean",
            "string": "a",
        }, AbstractDict(key_type=String()))
    ).value

    assert error.object_name == "[True]"
    assert error.object_type == bool


def test_abstract_dict_invalid_value_type():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate({
            False: 0,
            "string": "a",
        }, AbstractDict(value_type=String()))
    ).value

    assert error.object_name == "[False]"
    assert error.object_type == int



def test_dict_empty():
    _validate({}, Dict({}))


def test_dict_with_schema():
    _validate({
        False: "string",
        1: True,
        "integer": 10,
    }, Dict({
        False: String(),
        1: Bool(),
        "integer": Integer(),
        3.3: Float(optional=True),
    }))


def test_dict_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
       _validate([],  Dict({}))
    ).value

    assert error.object_name == ""
    assert error.object_type == list


def test_dict_unknown_parameter():
    error = pytest.raises(UnknownParameterError, lambda:
        _validate({
            1: True,
            False: "value",
        }, Dict({1: Bool()}))
    ).value

    assert error.object_name == "[False]"


def test_dict_missing_parameter():
    error = pytest.raises(MissingParameterError, lambda:
        _validate({
            2: "value",
        }, Dict({1: Bool(), 2: String()}))
    ).value

    assert error.object_name == "[1]"



def _validate(obj, scheme):
    obj_copy = copy.deepcopy(obj)

    try:
        validated = scheme.validate(obj)
    finally:
        assert obj == obj_copy

    assert validated is obj
