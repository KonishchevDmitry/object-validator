"""Test schema validation."""

from __future__ import unicode_literals

import copy
import sys

import pytest

from object_validator import Bool, Integer, Float, String, List, Dict, DictScheme, validate
from object_validator import InvalidTypeError, InvalidValueError, UnknownParameterError, MissingParameterError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


ITEMS = [{
    "id": 0,
    "name": "zero",
    "value": 0.0,
    "zero": True,
    "dividers": [],
    "dividers_map": {},
}, {
    "id": 2,
    "name": "two",
    "value": 2.0,
    "zero": False,
    "dividers": [1, 2],
    "dividers_map": {
        1: 1.0,
        2: 2.0,
    },
}]

SCHEME = List(DictScheme({
    "id": Integer(choices=(0, 2)),
    "name": String(),
    "value": Float(),
    "zero": Bool(),
    "dividers": List(Integer()),
    "dividers_map": Dict(Integer(), Float()),
}))



def test_validate():
    _validate("items", copy.deepcopy(ITEMS), SCHEME)


def test_validate_invalid_type():
    items = copy.deepcopy(ITEMS)
    items[1]["id"] = "string"

    error = pytest.raises(InvalidTypeError, lambda:
        _validate("items", items, SCHEME)
    ).value

    assert error.object_name == "items[1]['id']"
    assert error.object_type == str


def test_validate_invalid_value():
    items = copy.deepcopy(ITEMS)
    items[1]["id"] = 1

    error = pytest.raises(InvalidValueError, lambda:
        _validate("items", items, SCHEME)
    ).value

    assert error.object_name == "items[1]['id']"
    assert error.object_value == 1


def test_validate_unknown_parameter():
    items = copy.deepcopy(ITEMS)
    items[0][0] = 0

    assert pytest.raises(UnknownParameterError, lambda:
        _validate("items", items, SCHEME)
    ).value.object_name == "items[0][0]"


def test_validate_missing_parameter():
    items = copy.deepcopy(ITEMS)
    del items[1]["id"]

    assert pytest.raises(MissingParameterError, lambda:
        _validate("items", items, SCHEME)
    ).value.object_name == "items[1]['id']"



def _validate(name, obj, scheme):
    obj_copy = copy.deepcopy(obj)

    try:
        validated = validate(name, obj, scheme)
    finally:
        assert obj == obj_copy

    assert validated is obj
