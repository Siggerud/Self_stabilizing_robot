import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, ANY
from exceptions import YamlParseException
from os import path

@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")

@pytest.fixture
def xboxLoader(configDirPath):
    return ModuleLoader(configDirPath, "global_xbox")

@patch('moduleLoader.HonkHandling')
def test_setup_honk_handling_disabled(mock_honkHandling, audioLoader):
    honkHandler = audioLoader.setup_stabilizer("honk_disabled")

    assert honkHandler is None
    mock_honkHandling.assert_not_called()

@patch('moduleLoader.CarHandling')
def test_setup_car_handling_disabled(mock_carHandling, xboxLoader):
    carHandler = xboxLoader.setup_car_handling("car_handling_disabled")

    assert carHandler is None
    mock_carHandling.assert_not_called()


@patch('moduleLoader.CarHandling')
@patch('moduleLoader.MotorDriver')
def test_setup_car_handling_enabled(mock_motorDriver, mock_carHandling, xboxLoader):
    xboxLoader.setup_car_handling("car_handling_enabled")

    # motordriver data
    pins = {
        "IN1": 22,
        "IN2": 18,
        "IN3": 16,
        "IN4": 15,
        "ENA": 11,
        "ENB": 13
    }
    motors = {
        "Sides": {"MotorA": "right", "MotorB": "left"},
        "ReverseDirection": {"MotorA": False, "MotorB": False}
    }
    pwmValues = {
        "Minimum": 20, "Maximum": 60
    }

    motorDriver = mock_motorDriver.return_value
    speedStep = 6

    mock_motorDriver.assert_called_once_with(
        pins,
        motors,
        pwmValues
    )

    mock_carHandling.assert_called_once_with(
        motorDriver,
        speedStep,
        ANY,
        ANY
    )

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

    # motion tracking device data
    rollAxis = "x"
    pitchAxis = "y"
    offsets = {"x": 2.56, "y": 0}
    stabilizeOnStartup = False

    motionTrackingDevice = mock_motionTrackingDevice.return_value
    pca9685 = mock_pca9685.return_value
    tresholds = {"roll": 7, "pitch": 8}
    stabilizerChannels = {"frontRight": 6, "frontLeft": 7, "rearLeft": 9, "rearRight": 8}

    mock_pca9685.assert_called_once()

    mock_motionTrackingDevice.assert_called_once_with(
        rollAxis, pitchAxis, offsets, stabilizeOnStartup
    )

    mock_stabilizer.assert_called_once_with(
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
