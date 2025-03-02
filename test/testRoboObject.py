import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from roboObject import RoboObject
from exceptions import InvalidPinException, InvalidCommandException

@pytest.fixture(autouse=True)
def reset_robo_object():
    yield
    RoboObject._boardPinsInUse.clear()
    RoboObject._commandsInUse.clear()

def test_invalid_board_pin_exception():
    with pytest.raises(InvalidPinException):
        RoboObject([3, 5, 1], {"command": "my command"})

def test_duplicate_board_pin_exception():
    RoboObject([3, 5], {"command": "my command"})
    with pytest.raises(InvalidPinException):
        RoboObject([5, 7], {"command": "my command"})

def test_too_short_command_exception():
    with pytest.raises(InvalidCommandException):
        RoboObject([3, 5], {"command": "go"})

def test_duplicate_command_exception():
    RoboObject([3, 5], {"command": "my command"})
    with pytest.raises(InvalidCommandException):
        RoboObject([7, 11], {"command": "my command"})

