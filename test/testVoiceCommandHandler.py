import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from voiceCommandHandler import VoiceCommandHandler
from exceptions import InvalidCommandException

@pytest.fixture
def voiceHandler():
    return VoiceCommandHandler()

def test_get_camera_helper_commands(voiceHandler):
    commands: dict[str: str] = {
        "zoom": "zoom {notParam}",
        "turn_on_display": "a",
        "turn_off_display": "b",
        "zoom_in": "c",
        "zoom_out": "d"
    }
    with pytest.raises(InvalidCommandException):
        voiceHandler.get_camera_helper_commands(commands, 1.0, 2.0, 0.2)




