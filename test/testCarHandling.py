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
                    "turn left": CarHandlingCommand(movement="Left"),
                    "increase speed": CarHandlingCommand(speedChange=5),
                    "slow down": CarHandlingCommand(speedChange=-5)}

    return CarHandling(motorDriver, 30, 100, 10, userCommands)

@pytest.mark.parametrize("test_input,expected",
                         [("go forward now", "Forward"),
                          ("set reverse", "Reverse"),
                          ("turn left", "Left")])
def test_change_of_direction(carHandler, test_input, expected):
    carHandler.handle_command(test_input)

    assert carHandler.current_turn_value == expected


def test_increment_speed(carHandler):
    startSpeed = carHandler.current_speed
    carHandler.handle_command("increase speed")

    assert carHandler.current_speed == startSpeed + 5

    carHandler.handle_command("slow down")

    assert carHandler.current_speed == startSpeed
