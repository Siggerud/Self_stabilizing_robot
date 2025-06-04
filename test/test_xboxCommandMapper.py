import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from exceptions import InvalidCommandException
from commandMappers.xBoxCommandMapper import XBoxCommandMapper
from data.instructionContainers.carHandlingInstruction import CarHandlingInstruction
from data.instructionContainers.honkInstruction import HonkInstruction
from data.instructionContainers.cameraHelperInstruction import CameraHelperInstruction
from data.instructionContainers.cameraServoInstruction import CameraServoInstruction


@pytest.fixture
def commandMapper():
    return XBoxCommandMapper()


@pytest.mark.parametrize(
    "specInput,stickValueHorizontal,expectedStickInstructionHorizontal,stickValueVertical,expectedStickInstructionVertical",
    [
        ({"xbox": {"commands": {
            "move_horizontal": "lsb",
            "move_vertical": "lsb"
        }},
             "angle_limits_horizontal": {
                 "min_angle": -60,
                 "max_angle": 60
             },
             "angle_limits_vertical": {
                 "min_angle": -90,
                 "max_angle": 90
             }}, -0.5, 30, -0.5, 45),
        ({"xbox": {"commands": {
            "move_horizontal": "rsb",
            "move_vertical": "rsb"
        }},
             "angle_limits_horizontal": {
                 "min_angle": -10,
                 "max_angle": 20
             },
             "angle_limits_vertical": {
                 "min_angle": -50,
                 "max_angle": 50
             }}, -1.0, 20, -1.0, 50),
        ({"xbox": {"commands": {
            "move_horizontal": "lsb",
            "move_vertical": "lsb"
        }},
             "angle_limits_horizontal": {
                 "min_angle": -60,
                 "max_angle": 60
             },
             "angle_limits_vertical": {
                 "min_angle": -90,
                 "max_angle": 90
             }}, 0.0, 0, 0.0, 0),
    ])
def test_get_camera_servo_handling_commands(commandMapper, specInput, stickValueHorizontal,
                                            expectedStickInstructionHorizontal, stickValueVertical,
                                            expectedStickInstructionVertical):
    result: dict = commandMapper.get_camera_servo_handling_commands(specInput)

    # check that we have the right amount of commands
    assert get_num_of_key_matches_for_button(specInput["xbox"]["commands"]["move_horizontal"].upper() + " horizontal",
                                             result) == 201
    assert get_num_of_key_matches_for_button(specInput["xbox"]["commands"]["move_horizontal"].upper() + " vertical",
                                             result) == 201

    command = specInput["xbox"]["commands"][f"move_horizontal"].upper() + f" horizontal {stickValueHorizontal}"
    assert result[command] == CameraServoInstruction(horizontalAngle=expectedStickInstructionHorizontal)

    command = specInput["xbox"]["commands"][f"move_vertical"].upper() + f" vertical {stickValueVertical}"
    assert result[command] == CameraServoInstruction(verticalAngle=expectedStickInstructionVertical)


@pytest.mark.parametrize(
    "specInput,triggerValue,expectedTriggerInstruction,stickValue,direction,expectedStickInstruction", [
        ({"xbox": {"commands": {
            "drive": "rt",
            "reverse": "lt",
            "turning": "lsb"
        }}}, -1.0, 0, -0.75, "Left", 75),
        ({"xbox": {"commands": {
            "drive": "lt",
            "reverse": "rt",
            "turning": "rsb"
        }}}, 0.5, 75, 0.1, "Right", 10),
        ({"xbox": {"commands": {
            "drive": "lt",
            "reverse": "rt",
            "turning": "lsb"
        }}}, 1.0, 100, 1.0, "Right", 100),
    ])
def test_get_car_handling_commands(commandMapper, specInput, triggerValue, expectedTriggerInstruction, stickValue,
                                   direction, expectedStickInstruction):
    result: dict = commandMapper.get_car_handling_commands(specInput)

    # test that we get the expected number of commands for stick and trigger buttons
    assert get_num_of_key_matches_for_button(specInput["xbox"]["commands"]["drive"].upper(), result) == 201
    assert get_num_of_key_matches_for_button(specInput["xbox"]["commands"]["reverse"].upper(), result) == 201
    assert get_num_of_key_matches_for_button(specInput["xbox"]["commands"]["turning"].upper(), result) == 201

    command = specInput["xbox"]["commands"]["drive"].upper() + f" {triggerValue}"
    assert result[command] == CarHandlingInstruction(movement="Forward", speedValue=expectedTriggerInstruction)

    command = specInput["xbox"]["commands"]["turning"].upper() + f" horizontal {stickValue}"
    assert result[command] == CarHandlingInstruction(movement=direction, speedValue=expectedStickInstruction)


def get_num_of_key_matches_for_button(button: str, commands: dict) -> int:
    matchCounter: int = 0
    for key in list(commands.keys()):
        if button in key:
            matchCounter += 1

    return matchCounter


@pytest.mark.parametrize("spec_input,key,value", [
    ({"zoom": {"zoom_step": 0.1},
      "xbox": {"commands": {
          "turn_display_on_or_off": "b",
          "zoom_in": "d-pad up",
          "zoom_out": "d-pad down"}}}, "B press", CameraHelperInstruction(changeDisplayActive=True)),
    ({"zoom": {"zoom_step": 0.2},
      "xbox": {"commands": {
          "turn_display_on_or_off": "y",
          "zoom_in": "D-pad left",
          "zoom_out": "D-pad right"}}}, "D-PAD LEFT press", CameraHelperInstruction(zoomChange=0.2)),
])
def test_get_camera_helper_commands(commandMapper, spec_input, key, value):
    result: dict = commandMapper.get_camera_helper_commands(spec_input)

    assert result[key] == value


@pytest.mark.parametrize("spec_input,key,value", [
    ({"xbox": {"commands": {"honk": "x"}}}, "X press", HonkInstruction(startContinuousHonk=True)),
    ({"xbox": {"commands": {"honk": "A"}}}, "A release", HonkInstruction(stopContinuousHonk=True)),
])
def test_get_honk_commands(commandMapper, spec_input, key, value):
    result: dict = commandMapper.get_honk_commands(spec_input)

    assert result[key] == value


@pytest.mark.parametrize("spec_input,expected_output", [
    ({"xbox": {"commands": {"exit": "y"}}}, "Y press"),
    ({"xbox": {"commands": {"exit": "Back"}}}, "BACK press")
])
def test_get_exit_command(commandMapper, spec_input, expected_output):
    result: str = commandMapper.get_exit_command(spec_input)

    assert result == expected_output


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {"exit": "rt"}}},
    {"xbox": {"commands": {"exit": "D-PAD up"}}},
    {"xbox": {"commands": {"exit": "lsb"}}}
])
def test_push_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_exit_command(test_input)


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "RT",
        "zoom_out": "DRAD down"
    }}},
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "D-PAD up",
        "zoom_out": "x"
    }}},
    {"xbox": {"commands": {
        "turn_display_on_or_off": "A",
        "zoom_in": "D-PAD left",
        "zoom_out": "D-PAD left"
    }}}
])
def test_dpad_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_camera_helper_commands(test_input)


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "move_horizontal": "x",
        "move_vertical": "LSB"
    }}},
    {"xbox": {"commands": {
        "move_horizontal": "x",
        "move_vertical": "d-pad down"
    }}}
])
def test_sticks_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_camera_servo_handling_commands(test_input)


@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {
        "drive": "x",
        "reverse": "a"
    }}},
    {"xbox": {"commands": {
        "drive": "rt",
        "reverse": "lsb"
    }}},
    {"xbox": {"commands": {
        "drive": "lt",
        "reverse": "lt"
    }}}
])
def test_trigger_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_car_handling_commands(test_input)
