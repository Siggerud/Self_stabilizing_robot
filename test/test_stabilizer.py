import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock, call
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

@pytest.fixture
def stabilizer(motionTrackingDevice, pca9685, channels):
    return Stabilizer(motionTrackingDevice, pca9685, 5, 5, channels)

@pytest.mark.parametrize("servoChannel, angle, rollAndPitch",
                         [(1, 1, (-6, 10)),
                          (3, 179, (6, 12)),
                          (0, 179, (-6, -8)),
                          (2, 1, (20, -40))
                          ])
def test_stabilize_pitch_and_roll(stabilizer, motionTrackingDevice, pca9685, servoChannel, angle, rollAndPitch):
    motionTrackingDevice.get_roll_and_pitch.return_value = rollAndPitch

    stabilizer.stabilize()

    pca9685.set_servo_to_angle.assert_called_once_with(servoChannel, angle)

@pytest.mark.parametrize("servoChannels, angles, pitch",
                         [((1, 3), (1, 179), 6),
                          ((0, 2), (179, 1), -10)])
def test_stabilize_pitch(stabilizer, motionTrackingDevice, pca9685, servoChannels, angles, pitch):
    motionTrackingDevice.get_roll_and_pitch.return_value = (-4, pitch)

    stabilizer.stabilize()

    calls = [call(servoChannels[0], angles[0]), call(servoChannels[1], angles[1])]
    pca9685.set_servo_to_angle.assert_has_calls(calls, any_order=True)

@pytest.mark.parametrize("servoChannels, angles, roll",
                         [((0, 1), (179, 1), -6),
                          ((2, 3), (1, 179), 7)])
def test_stabilize_roll(stabilizer, motionTrackingDevice, pca9685, servoChannels, angles, roll):
    motionTrackingDevice.get_roll_and_pitch.return_value = (roll, 4)

    stabilizer.stabilize()

    calls = [call(servoChannels[0], angles[0]), call(servoChannels[1], angles[1])]
    pca9685.set_servo_to_angle.assert_has_calls(calls, any_order=True)

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
