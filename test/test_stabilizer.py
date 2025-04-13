import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock
from stabilizer import Stabilizer
from exceptions import StabilizerException

@pytest.fixture
def pca9685():
    return Mock()

@pytest.fixture
def motionTrackingDevice():
    return Mock()

@pytest.fixture
def channels():
    return {
        "frontLeft": 0,
        "rearLeft": 1,
        "frontRight": 2,
        "rearRight": 3}

def test_stabilize(pca9685, motionTrackingDevice, channels):
    stabilizer = Stabilizer(motionTrackingDevice, pca9685, 5, 5, channels)
    motionTrackingDevice.get_roll_and_pitch.return_value = (-6, 4)

    stabilizer.stabilize()

    # since it rolls to the right, we expect the left side to be lowered
    pca9685.set_servo_to_angle.assert_called_once_with(channel=0, angle=179)
    pca9685.set_servo_to_angle.assert_called_once_with(channel=1, angle=1)

@pytest.mark.parametrize("rollAndPitch, tresholds",
                         [((1, 1), (2, 2)),
                          ((1, 4), (2, 5)),
                          ((80, 80), (81, 81))
                          ])
def test_stabilize_tresholds(pca9685, motionTrackingDevice, channels, rollAndPitch, tresholds):
    stabilizer = Stabilizer(motionTrackingDevice, pca9685, tresholds[0], tresholds[1], channels)
    motionTrackingDevice.get_roll_and_pitch.return_value = rollAndPitch

    stabilizer.stabilize()

    #pca9685 should not be called if angles are below tresholds
    pca9685.set_servo_to_angle.assert_not_called()

@pytest.mark.parametrize("test_input",
                         [[0, 91],
                         [91, 0],
                          [-5, 1],
                          [-5, 5],
                          [100, 92]])
def test_validate_input_raise_error_on_tresholds(pca9685, motionTrackingDevice, channels, test_input):
    rollTreshold, pitchTreshold = test_input

    with pytest.raises(StabilizerException):
        Stabilizer(motionTrackingDevice, pca9685, rollTreshold, pitchTreshold, channels)

@pytest.mark.parametrize("test_input",
                         [[0, 1, 3, 1],
                         [1, 1, 1, 1],
                         [0, 1, 2, 16],
                         [-1, 0, 1, 2]])
def test_validate_input_raise_error_on_channel_input(pca9685, motionTrackingDevice, test_input):
    channels = {
        "frontLeft": test_input[0],
        "rearLeft": test_input[1],
        "frontRight": test_input[2],
        "rearRight": test_input[3]}

    with pytest.raises(StabilizerException):
        Stabilizer(motionTrackingDevice, pca9685, 3, 3, channels)
