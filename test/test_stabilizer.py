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

@pytest.mark.parametrize("roll, pitch, tresholds",
                         [(2, 2, [3, 3]),
                          (2, 5, [1, 4]),
                          (80, 80, [81, 81])
                          ])
def test_stabilize_tresholds(pca9685, motionTrackingDevice, roll, pitch, tresholds):
    channels = {
        "frontLeft": 0,
        "rearLeft": 1,
        "frontRight": 2,
        "rearRight": 3}

    stabilizer = Stabilizer(motionTrackingDevice, pca9685, roll, pitch, channels)
    motionTrackingDevice.get_roll_and_pitch.return_value = tresholds

    stabilizer.stabilize()

    #pca9685 should not be called if angles are below tresholds
    pca9685.set_servo_to_angle.assert_not_called()

@pytest.mark.parametrize("test_input",
                         [[0, 91],
                         [91, 0],
                          [-5, 1],
                          [-5, 5],
                          [100, 92]])
def test_validate_input_raise_error_on_tresholds(pca9685, motionTrackingDevice, test_input):
    channels = {
        "frontLeft": 0,
        "rearLeft": 1,
        "frontRight": 2,
        "rearRight": 3}
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
