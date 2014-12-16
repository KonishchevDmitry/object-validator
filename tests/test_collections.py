"""Test collection types validation."""

from __future__ import unicode_literals

import copy
import sys

import pytest

from object_validator import Object, Bool, Integer, Float, String, List, Dict, DictScheme
from object_validator import InvalidTypeError, MissingParameterError, UnknownParameterError, ParameterAlreadyExistsError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


class ToInt(Object):
    def validate(self, obj):
        return int(obj)



def test_list_empty():
    _validate([], List(Bool()))


def test_list_full():
    _validate([True, False], List(Bool()))


def test_list_without_scheme():
    _validate(["string"], List())


def test_list_modification():
    _validate_modification(["1", "2"], List(ToInt()), [1, 2])


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



def test_dict_default():
    _validate({
        True: 1,
        0: False,
        3.3: "float",
        "string": "string",
    }, Dict())


def test_dict_key_value():
    _validate({
        "one": 1.0,
        "two": 2.0,
    }, Dict(String(), Float()))


def test_dict_key_modification():
    _validate_modification(
        { "1": 10, "2": 20 }, Dict(ToInt(), Integer()), { 1: 10, 2: 20 })


def test_dict_value_modification():
    _validate_modification(
        { 1: "10", 2: "20" }, Dict(Integer(), ToInt()), { 1: 10, 2: 20 })


def test_dict_key_value_modification():
    _validate_modification(
        { "1": "10", "2": "20" }, Dict(ToInt(), ToInt()), { 1: 10, 2: 20 })


def test_dict_invalid_key_modification():
    error = pytest.raises(ParameterAlreadyExistsError, lambda:
        _validate_modification(
            { 1: "10", "1": "100" }, Dict(ToInt(), None), { 1: 10 })
    ).value

    assert error.object_name == "[1]"


def test_dict_invalid_key_scheme():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate({
            True: "boolean",
            "string": "a",
        }, Dict(key_scheme=String()))
    ).value

    assert error.object_name == "[True]"
    assert error.object_type == bool


def test_dict_invalid_value_scheme():
    error = pytest.raises(InvalidTypeError, lambda:
        _validate({
            False: 0,
            "string": "a",
        }, Dict(value_scheme=String()))
    ).value

    assert error.object_name == "[False]"
    assert error.object_type == int



def test_dict_scheme_empty():
    _validate({}, DictScheme({}))


def test_dict_scheme_with_schema():
    _validate({
        False: "string",
        1: True,
        "integer": 10,
        4.4: 44.4,
    }, DictScheme({
        False: String(),
        1: Bool(),
        "integer": Integer(),
        3.3: Float(optional=True),
        4.4: Float(optional=True),
    }))


def test_dict_scheme_with_ignore_unknown():
    _validate({
        "known_key": 10,
        "unknown_key": 10,
    }, DictScheme({"known_key": Integer()}, ignore_unknown=True))


def test_dict_scheme_with_delete_unknown():
    _validate_modification(
        {"known_key": 10, "unknown_key": 10,},
        DictScheme({"known_key": Integer()}, delete_unknown=True),
        {"known_key": 10})


def test_dict_scheme_modification():
    _validate_modification(
        { "1": "10", "2": "20", "3": "30" },
        DictScheme({ "1": ToInt(), "2": String(), "3": ToInt() }),
        { "1": 10, "2": "20", "3": 30 })


def test_dict_scheme_invalid_type():
    error = pytest.raises(InvalidTypeError, lambda:
       _validate([],  DictScheme({}))
    ).value

    assert error.object_name == ""
    assert error.object_type == list


def test_dict_scheme_unknown_parameter():
    error = pytest.raises(UnknownParameterError, lambda:
        _validate({
            1: True,
            False: "value",
        }, DictScheme({1: Bool()}))
    ).value

    assert error.object_name == "[False]"


def test_dict_scheme_missing_parameter():
    error = pytest.raises(MissingParameterError, lambda:
        _validate({
            2: "value",
        }, DictScheme({1: Bool(), 2: String()}))
    ).value

    assert error.object_name == "[1]"



def _validate(obj, scheme):
    obj_copy = copy.deepcopy(obj)

    try:
        validated = scheme.validate(obj)
    finally:
        assert obj == obj_copy

    assert validated is obj


def _validate_modification(obj, scheme, new_obj):
    validated = scheme.validate(obj)
    assert validated is obj
    assert validated == new_obj
