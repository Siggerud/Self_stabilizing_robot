import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock
from stabilizer import Stabilizer
from exceptions import StabilizerException

@pytest.mark.parametrize("test_input",
                         [[0, 91],
                         [91, 0],
                          [-5, 1],
                          [-5, 5],
                          [100, 92]])
def test_validate_input_raise_error_on_tresholds(test_input):
    pca9695 = Mock()
    motionTrackingDevice = Mock()
    channels = {
        "frontLeft": 0,
        "rearLeft": 1,
        "frontRight": 2,
        "rearRight": 3}
    rollTreshold, pitchTreshold = test_input

    with pytest.raises(StabilizerException):
        Stabilizer(motionTrackingDevice, pca9695, rollTreshold, pitchTreshold, channels)

@pytest.mark.parametrize("test_input",
                         [[0, 1, 3, 1],
                         [1, 1, 1, 1],
                         [0, 1, 2, 16],
                         [-1, 0, 1, 2]])
def test_validate_input_raise_error_on_channel_input(test_input):
    pca9695 = Mock()
    motionTrackingDevice = Mock()
    channels = {
        "frontLeft": test_input[0],
        "rearLeft": test_input[1],
        "frontRight": test_input[2],
        "rearRight": test_input[3]}

    with pytest.raises(StabilizerException):
        Stabilizer(motionTrackingDevice, pca9695, 3, 3, channels)
