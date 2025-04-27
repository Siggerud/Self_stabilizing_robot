import os
import sys

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

    carSpecs = {
        "audio": {
            "commands": commands,
            "command_descriptions": descriptions
        }
    }

    result = voiceHandler.get_command_descriptions(carSpecs)

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

    angleLimitsHorizontal = {
        "min_angle": -60,
        "max_angle": 60
    }

    angleLimitsVertical = {
        "min_angle": -60,
        "max_angle": 60
    }


    cameraServoSpecs = {
        "audio": {
            "commands": commands,
            "command_descriptions": {},
            "angle_limits_vertical": angleLimitsVertical,
            "angle_limits_horizontal": angleLimitsHorizontal
        }
    }

    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_servo_handling_commands(cameraServoSpecs)


def test_get_camera_helper_commands_param_check(voiceHandler):
    commands: dict[str: str] = {
        "zoom": "zoom {notParam}",
        "turn_on_display": "a a",
        "turn_off_display": "b b",
        "zoom_in": "c b",
        "zoom_out": "d d"
    }

    cameraSpecs = {
        "audio": {
            "commands": commands,
            "command_descriptions": {},
            "zoom": {
                "max_zoom_value": 5,
                "zoom_step": 0.1
            }
        }
    }

    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_helper_commands(cameraSpecs)


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

    carSpecs = {
        "audio": {
            "commands": commands,
            "command_descriptions": {},
            "Other": {
                "speed_step": 12
            }
        }
    }

    with pytest.raises(InvalidCommandException):
        voiceHandler.get_car_handling_commands(carSpecs)
