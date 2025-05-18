import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, MagicMock
from exceptions import YamlParseException
from os import path

@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")

@pytest.fixture
def xboxLoader(configDirPath):
    return ModuleLoader(configDirPath, "global_xbox")

@patch('moduleLoader.Stabilizer')
def test_setup_stabilizer_disabled(mock_stabilizer, xboxLoader):
    stabilizer = xboxLoader.setup_stabilizer("stabilizer_disabled")

    assert stabilizer is None
    mock_stabilizer.assert_not_called()

@patch('moduleLoader.Stabilizer')
@patch('moduleLoader.PCA9685')
@patch('moduleLoader.MotionTrackingDevice')
def test_setup_stabilizer_enabled(mock_motionTrackingDevice, mock_pca9685, mock_stabilizer, xboxLoader):
    xboxLoader.setup_stabilizer("stabilizer_enabled")

    motionTrackingDevice = mock_motionTrackingDevice.return_value
    pca9685 = mock_pca9685.return_value
    tresholds = {"roll": 7, "pitch": 8}
    stabilizerChannels = {"frontRight": 6, "frontLeft": 7, "rearLeft": 9, "rearRight": 8}

    mock_stabilizer.assert_called_with(
        motionTrackingDevice,
        pca9685,
        tresholds,
        stabilizerChannels
    )

@patch('moduleLoader.AudioHandler')
def test_setup_command_generator_audio(mock_audio_handler, configDirPath):
    loader = ModuleLoader(configDirPath, "global_audio")

    loader.setup_command_generator()

    mock_audio_handler.assert_called_once()

@patch('moduleLoader.XBoxEventHandler')
def test_setup_command_generator_xbox(mock_xbox_handler, configDirPath):
    loader = ModuleLoader(configDirPath, "global_xbox")

    loader.setup_command_generator()

    mock_xbox_handler.assert_called_once()

def test_error_handling_of_invalid_config_files(xboxLoader):
    with pytest.raises(YamlParseException):
        xboxLoader.setup_car_handling("car_racing")
