import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from carHandling import CarHandling
from motorDriver import MotorDriver
from commandContainers.carHandlingCommands import CarHandlingCommand
from unittest.mock import patch, Mock

@pytest.fixture
def carHandler():
    motorDriver = Mock()
    userCommands = {"go forward now": CarHandlingCommand(movement="Forward")}

    return CarHandling(motorDriver, 0, 100, 10, userCommands)

def test_change_of_direction(carHandler):
    carHandler.handle_command("go forward now")

    assert carHandler.current_turn_value == "Forward"
