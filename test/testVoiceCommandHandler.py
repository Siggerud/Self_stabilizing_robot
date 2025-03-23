import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from voiceCommandHandler import VoiceCommandHandler

@pytest.fixture
def voiceHandler():
    return VoiceCommandHandler()

def test_get_camera_helper_commands():
    #TODO: implement test
    pass




