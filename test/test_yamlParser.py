import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from utility.yamlParser import get_bool, get_int, get_float, get_yaml_content_from_file
from exceptions import YamlParseException


def test_get_yaml_content_from_file():
    filepath = os.path.join(os.path.dirname(__file__), "resources/testYaml.yml")

    expected = {
        "enabled": True,
        "my_word": "Hello there",
        "top_nest": {
            "middle_nest": {
                "inner_nest": "nested_value"
            }
        },
        "my_number": 52,
        "my_float": 1.3
    }

    result = get_yaml_content_from_file(filepath)

    assert expected == result

def test_get_yaml_content_from_file_raises_error():
    invalidFilepath = os.path.join(os.path.dirname(__file__), "resources/nonExistentYaml.yml")
    with pytest.raises(YamlParseException):
        get_yaml_content_from_file(invalidFilepath)

@pytest.mark.parametrize("specs,key,expected", [
    ({"displayOn": "True", "speed": "50"}, "displayOn", True),
    ({"displayOff": False, "gear": 2}, "displayOff", False)
])
def test_get_bool(specs, key, expected):
    assert get_bool(specs, key) == expected


@pytest.mark.parametrize("specs,key", [
    ({"displayOn": "true", "speed": "50"}, "language"),
    ({"displayOff": "yes", "gear": 2}, "displayOff")
])
def test_get_bool_raising_error(specs, key):
    with pytest.raises(YamlParseException):
        get_bool(specs, key)


@pytest.mark.parametrize("specs,key,expected", [
    ({"gears": "8", "speed": "50"}, "gears", 8),
    ({"speed": 70, "gear": 2}, "speed", 70)
])
def test_get_int(specs, key, expected):
    assert get_int(specs, key) == expected


@pytest.mark.parametrize("specs,key", [
    ({"steps": "ten", "speed": "50"}, "steps"),
    ({"wheels": True, "gear": 2}, "wheels")
])
def test_get_int_raises_error(specs, key):
    with pytest.raises(YamlParseException):
        get_int(specs, key)


@pytest.mark.parametrize("specs,key,expected", [
    ({"maxZoom": "8.3", "speed": "50"}, "maxZoom", 8.3),
    ({"speed": 70, "gear": 2}, "speed", 70.0)
])
def test_get_float(specs, key, expected):
    assert get_float(specs, key) == expected


@pytest.mark.parametrize("specs,key", [
    ({"steps": "forty", "speed": "50"}, "steps"),
    ({"wheels": False, "gear": 2}, "wheels")
])
def test_get_float_raises_error(specs, key):
    with pytest.raises(YamlParseException):
        get_float(specs, key)
