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
    userCommands = {"go forward now": CarHandlingCommand(movement="Forward"),
                    "set reverse": CarHandlingCommand(movement="Reverse"),
                    "turn left": CarHandlingCommand(movement="Left")}

    return CarHandling(motorDriver, 0, 100, 10, userCommands)

@pytest.mark.parametrize("test_input,expected",
                         [("go forward now", "Forward"),
                          ("set reverse", "Reverse"),
                          ("turn left", "Left")])
def test_change_of_direction(carHandler, test_input, expected):
    carHandler.handle_command(test_input)

    assert carHandler.current_turn_value == expected
