import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock
from stabilizer import Stabilizer
from exceptions import StabilizerException

@pytest.mark.parametrize("test_input",
                         [[0, 1, 3, 2]])
def test_validate_input_raise_error_on_duplicates(test_input):
    pca9695 = Mock()
    motionTrackingDevice = Mock()
    print(test_input)
    channels = {
        "frontLeft": test_input[0],
        "rearLeft": test_input[1],
        "frontRight": test_input[2],
        "rearRight": test_input[0]}

    with pytest.raises(StabilizerException):
        Stabilizer(motionTrackingDevice, pca9695, 3, 3, channels)
