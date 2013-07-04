"""Test complex schema validation."""

from __future__ import unicode_literals

import copy
import sys

import pytest

from json_validator import Bool, Integer, Float, String, List, AbstractDict, Dict, validate
from json_validator import UnknownParameterError

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_complex_schema():
    items = [{
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

    items_scheme = List(Dict({
        "id": Integer(),
        "name": String(),
        "value": Float(),
        "zero": Bool(),
        "dividers": List(Integer()),
        "dividers_map": AbstractDict(Integer(), Float()),
    }))

    assert validate("items", copy.deepcopy(items), items_scheme) == items

    items[0][0] = 0
    new_items = copy.deepcopy(items)
    assert pytest.raises(UnknownParameterError, lambda:
        validate("items", new_items, items_scheme)
    ).value.object_name == "items[0][0]"
