import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from exceptions import InvalidCommandException
from xBoxCommandMapper import XBoxCommandMapper
from data.commandContainers.carHandlingCommands import CarHandlingCommand


@pytest.fixture
def commandMapper():
    return XBoxCommandMapper()

@pytest.mark.parametrize("spec_input,key,value", [
    ({"xbox": {"commands": {"honk": "x"}}}, "X press", CarHandlingCommand(startContinuousHonk=True)),
    ({"xbox": {"commands": {"honk": "A"}}}, "A release", CarHandlingCommand(stopContinuousHonk=True)),
])
def test_get_honk_commands(commandMapper, spec_input, key, value):
    result: dict = commandMapper.get_honk_commands()

    assert result[key] == value

@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {"exit": "rt"}}},
    {"xbox": {"commands": {"exit": "D-PAD up"}}},
    {"xbox": {"commands": {"exit": "lsb"}}}
])
def test_push_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_exit_command(test_input)


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "RT",
        "zoom_out": "DRAD down"
    }}},
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "D-PAD up",
        "zoom_out": "x"
    }}},
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "D-PAD left",
        "zoom_out": "D-PAD left"
    }}}
])
def test_dpad_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_camera_helper_commands(test_input)


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "move_horizontal": "x",
        "move_vertical": "LSB"
    }}},
    {"xbox": {"commands": {
        "move_horizontal": "x",
        "move_vertical": "d-pad down"
    }}},
    {"xbox": {"commands": {
        "move_horizontal": "RSB",
        "move_vertical": "RSB"
    }}}
])
def test_sticks_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_camera_servo_handling_commands(test_input)

@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "drive": "x",
        "reverse": "a"
    }}},
    {"xbox": {"commands": {
        "drive": "rt",
        "reverse": "lsb"
    }}},
    {"xbox": {"commands": {
        "drive": "lt",
        "reverse": "lt"
    }}}
])
def test_trigger_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_car_handling_commands(test_input)
