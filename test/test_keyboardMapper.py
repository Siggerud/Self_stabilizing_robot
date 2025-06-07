import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from commandMappers.keyboardMapper import KeyboardMapper
from exceptions import InvalidCommandException


@pytest.fixture
def commandMapper():
    return KeyboardMapper()


@pytest.mark.parametrize("spec_input,expected_output", [
    ({"keyboard": {"commands": {"exit": "x"}}}, "x"),
    ({"keyboard": {"commands": {"exit": "esc"}}}, "esc")
])
def test_get_exit_command(commandMapper, spec_input, expected_output):
    result: str = commandMapper.get_exit_command(spec_input)

    assert result == expected_output


def test_valid_key_check(commandMapper):
    specInput = {"keyboard": {
        "default_speed": 100,
        "commands": {
            "turn_left": "a",
            "turn_right": "d",
            "drive": "ctrl",
            "reverse": "s"
        },
        "command_descriptions": {
            "turn_left": "Turns car left",
            "turn_right": "Turns car right",
            "drive": "Drives car forward",
            "reverse": "Reverses car"
        }
    }}
    with pytest.raises(InvalidCommandException):
        commandMapper.get_car_handling_commands(specInput)
