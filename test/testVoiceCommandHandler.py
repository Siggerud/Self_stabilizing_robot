import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from voiceCommandHandler import VoiceCommandHandler
from exceptions import InvalidCommandException

@pytest.fixture
def voiceHandler():
    return VoiceCommandHandler()

def test_get_camera_helper_commands_param_check(voiceHandler):
    commands: dict[str: str] = {
        "zoom": "zoom {notParam}",
        "turn_on_display": "a",
        "turn_off_display": "b",
        "zoom_in": "c",
        "zoom_out": "d"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_helper_commands(commands, 1.0, 2.0, 0.2)

def test_get_car_handling_commands_param_check(voiceHandler):
    commands: dict[str: str] = {
        "go_forward": "go forward",
        "go_backward": "go backward",
        "turn_left": "turn left",
        "turn_right": "turn right",
        "stop": "stop",
        "increase_speed": "increase speed",
        "decrease_speed": "increase speed",
        "set_speed": "set speed {param}"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_car_handling_commands(commands, 5, 10, 100)




