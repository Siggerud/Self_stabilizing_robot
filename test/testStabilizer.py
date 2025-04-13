import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock
from stabilizer import Stabilizer
from exceptions import StabilizerException


def test_validate_input_raise_error_on_duplicates():
    pca9695 = Mock()
    motionTrackingDevice = Mock()
    channels = {
        "frontLeft": 0,
        "rearLeft": 1,
        "frontRight": 1,
        "rearRight": 2}

    with pytest.raises(StabilizerException):
        stabilizer = Stabilizer(motionTrackingDevice, pca9695, 3, 3, channels)
