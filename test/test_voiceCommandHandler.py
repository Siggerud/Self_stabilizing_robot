import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from voiceCommandMapper import VoiceCommandMapper
from exceptions import InvalidCommandException
from data.commandContainers.carHandlingCommands import CarHandlingCommand

@pytest.fixture
def voiceHandler():
    return VoiceCommandMapper()

def test_command_descriptions(voiceHandler):
    commands = {"forward_command": "go forward",
                "reverse_command": "reverse"}

    descriptions = {"forward_command": "Move the car forward",
                    "reverse_command": "Move the car backward"}

    result = voiceHandler.get_command_descriptions(commands, descriptions)

    assert result == {"go forward": "Move the car forward",
                     "reverse": "Move the car backward"}

def test_get_camera_servo_handling_command_length_check(voiceHandler):
    commands: dict[str: str] = {
        "look_up": "look",
        "look_down": "look down",
        "look_left": "look left",
        "look_right": "look right",
        "look_center": "look center",
        "look_up_exact": "look up {param}",
        "look_down_exact": "look down {param}",
        "look_left_exact": "look left {param}",
        "look_right_exact": "look right {param}"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_servo_handling_commands(commands, {"horizontal": -90, "vertical": -90}, {"horizontal": 90, "vertical": 90})

def test_get_camera_helper_commands_param_check(voiceHandler):
    commands: dict[str: str] = {
        "zoom": "zoom {notParam}",
        "turn_on_display": "a a",
        "turn_off_display": "b b",
        "zoom_in": "c b",
        "zoom_out": "d d"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_helper_commands(commands, 1.0, 2.0, 0.2)

def test_get_car_handling_commands_param_check(voiceHandler):
    commands: dict[str: str] = {
        "drive": "go forward",
        "reverse": "go backward",
        "turn_left": "turn left",
        "turn_right": "turn right",
        "stop": "stop",
        "increase_speed": "increase speed",
        "decrease_speed": "increase speed",
        "exact_speed": "set speed {param}"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_car_handling_commands(commands, 5)




