import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from buzzer import Buzzer
from roboObject import RoboObject
from unittest.mock import patch

@pytest.fixture
def buzzer():
    return Buzzer(38, 0.3, 4, {"buzzCommand": "start honking", "buzzForSpecifiedTimeCommand": "honk {param}"})

def test_get_command_validity(buzzer):
    assert buzzer.get_command_validity("my command") == "valid"

@pytest.fixture(autouse=True)
def reset_robo_object():
    yield
    RoboObject._boardPinsInUse.clear()
    RoboObject._commandsInUse.clear()

@patch("RPi.GPIO.output")
@patch("buzzer.sleep")
def test_buzz_time(mockSleep, mockGpioOutput, buzzer):
    buzzer.handle_voice_command("start honking")

    mockGpioOutput.assert_called()
    mockSleep.assert_called_once_with(0.3)