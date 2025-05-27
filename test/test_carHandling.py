import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from carHandling import CarHandling
from hardware.motorDriver import MotorDriver
from data.instructionContainers.carHandlingInstruction import CarHandlingInstruction
from unittest.mock import Mock
from exceptions import OutOfRangeException


@pytest.fixture
def carHandler():
    motorDriver = Mock()
    userCommands = {"go forward now": CarHandlingInstruction(movement="Forward"),
                    "set reverse": CarHandlingInstruction(movement="Reverse"),
                    "turn left": CarHandlingInstruction(movement="Left"),
                    "stop the car": CarHandlingInstruction(movement="Stopped"),
                    "increase speed": CarHandlingInstruction(speedChange=5),
                    "slow down": CarHandlingInstruction(speedChange=-5),
                    "speed 30": CarHandlingInstruction(speedValue=30),
                    "speed 0": CarHandlingInstruction(speedValue=0),
                    "20 speed": CarHandlingInstruction(speedValue=20),
                    "go to 55": CarHandlingInstruction(speedValue=55),
                    "LSB 0.57": CarHandlingInstruction(speedValue=60, movement="Left"),
                    "LSB 0.0": CarHandlingInstruction(speedValue=0, movement="Stopped"),
                    "LSB -1.0": CarHandlingInstruction(speedValue=100, movement="Right"),
                    "RT -0.4": CarHandlingInstruction(speedValue=30, movement="Forward")}

    return CarHandling(motorDriver, 10, userCommands, {})


@pytest.mark.parametrize("test_input", [
    -1, 101
])
def test_argument_validity_checks(test_input):
    motorDriver = Mock()
    with pytest.raises(OutOfRangeException):
        CarHandling(motorDriver, test_input, {}, {})


@pytest.mark.parametrize("test_input,expected",
                         [("speed 0", "partially valid"),
                          ("20 speed", "valid"),
                          ("increase speed", "valid"),
                          ("slow down", "partially valid"),
                          ("turn left", "valid"),
                          ("stop the car", "partially valid")])
def test_validity_checks(carHandler, test_input, expected):
    result = carHandler.get_command_validity(test_input)

    assert result == expected


@pytest.mark.parametrize("test_input,expected",
                         [("speed 30", 30),
                          ("20 speed", 20),
                          ("go to 55", 55)])
def test_set_exact_speed(carHandler, test_input, expected):
    carHandler.handle_command(test_input)

    assert carHandler.current_speed == expected


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


@pytest.mark.parametrize("command,expectedDirection,expectedSpeed",
                         [("LSB 0.57", "Left", 60),
                          ("LSB 0.0", "Stopped", 0),
                          ("LSB -1.0", "Right", 100),
                          ("RT -0.4", "Forward", 30)
                          ]
                         )
def test_speed_change_and_direction_change(carHandler, command, expectedDirection, expectedSpeed):
    carHandler.handle_command(command)

    assert carHandler.current_turn_value == expectedDirection
    assert carHandler.current_speed == expectedSpeed

