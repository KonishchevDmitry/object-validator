"""Test collection types validation."""

from __future__ import unicode_literals

import sys

import pytest

from json_validator import Bool, Integer, Float, String, List, Dict
from json_validator import InvalidType, MissingParameter, UnknownParameter

PY2 = sys.version_info < (3,)
if PY2:
    str = unicode


def test_list():
    List(Bool()).validate("obj", [])
    List(Bool()).validate("obj", [True, False])

    assert pytest.raises(InvalidType, lambda:
        List(Bool()).validate("list", tuple())
    ).value.object_name == "list"

    assert pytest.raises(InvalidType, lambda:
        List(Bool()).validate("list", [False, 10, True])
    ).value.object_name == "list[1]"


def test_dict():
    Dict({}).validate("obj", {})

    Dict({
        False: String(),
        1: Bool(),
        "integer": Integer(),
    }).validate("obj", {
        False: "string",
        1: True,
        "integer": 10,
    })

    assert pytest.raises(InvalidType, lambda:
        Dict({}).validate("dict", object())
    ).value.object_name == "dict"

    assert pytest.raises(UnknownParameter, lambda:
        Dict({1: Bool()}).validate("dict", {
            1: True,
            False: "value",
        })
    ).value.object_name == "dict[False]"

    assert pytest.raises(MissingParameter, lambda:
        Dict({1: Bool(), 2: String()}).validate("dict", {
            2: "value",
        })
    ).value.object_name == "dict[1]"
