import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, ANY, call, Mock
from exceptions import YamlParseException
from os import path

@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")

@pytest.fixture
def xboxLoader(configDirPath):
    return ModuleLoader(configDirPath, "global_xbox")

@pytest.fixture
def audioLoader(configDirPath):
    return ModuleLoader(configDirPath, "global_audio")

@patch('moduleLoader.CommandHandler')
@patch('moduleLoader.CameraHelper')
def test_setup_command_handler(mock_cameraHelper, mock_commandHandler, audioLoader):
    camera = Mock()
    car = Mock()
    servo = None
    cameraHandler = Mock()
    honk = Mock()
    signalLights = Mock()

    audioLoader.setup_command_handler(
        camera,
        car,
        servo,
        cameraHandler,
        honk,
        signalLights
    )

    # check that camera helper was called, since camera is not None
    mock_cameraHelper.assert_called_once_with(
        ANY,
        cameraHandler,
        car,
        servo
    )

    # command handler data
    mockCameraHelperInstance = mock_cameraHelper.return_value
    exitCommand = "cancel program"

    mock_commandHandler.assert_called_once_with(
        [car, cameraHandler, honk],
        mockCameraHelperInstance,
        signalLights,
        exitCommand
    )

@patch('moduleLoader.CommandHandler')
def test_setup_command_handler_with_no_command_executors(mock_commandHandler, audioLoader):
    camera = Mock()
    car = None
    servo = None
    cameraHandler = None
    honk = None
    signalLights = Mock()

    commandHandler = audioLoader.setup_command_handler(
        camera,
        car,
        servo,
        cameraHandler,
        honk,
        signalLights
    )

    assert commandHandler is None
    mock_commandHandler.assert_not_called()

@patch('moduleLoader.CameraServoHandling')
def test_setup_servo_disabled(mock_cameraServoHandling, audioLoader):
    cameraServoHandler = audioLoader.setup_camera_servo_handling("servo_disabled")

    assert cameraServoHandler is None
    mock_cameraServoHandling.assert_not_called()

@patch('moduleLoader.CameraServoHandling')
@patch('moduleLoader.Servo')
def test_setup_servo_enabled(mock_servo, mock_cameraServoHandling, audioLoader):
    audioLoader.setup_camera_servo_handling("servo_enabled")

    # servo data
    horizontalServoPin = 35
    verticalServoPin = 16
    servoCalls = [call(horizontalServoPin), call(verticalServoPin)]

    # check that servos have been called with pins from yaml file
    mock_servo.assert_has_calls(servoCalls)

    # camera servo handler data
    mock_servoInstance = mock_servo.return_value
    minAngles = {
        "horizontal": -65,
        "vertical": -50
    }
    maxAngles = {
        "horizontal": 65,
        "vertical": 85
    }

    mock_cameraServoHandling.assert_called_once_with(
        mock_servoInstance,
        mock_servoInstance,
        minAngles,
        maxAngles,
        ANY,
        ANY
    )

@patch('moduleLoader.SignalLights')
def test_setup_signal_lights_disabled(mock_signalLights, audioLoader):
    signalLights = audioLoader.setup_signal_lights("signal_lights_disabled")

    assert signalLights is None
    mock_signalLights.assert_not_called()

@patch('moduleLoader.SignalLights')
def test_setup_signal_lights_enabled(mock_signalLights, audioLoader):
    audioLoader.setup_signal_lights("signal_lights_enabled")

    greenPin = 32
    yellowPin = 31
    redPin = 29
    blinkTime = 0.3

    mock_signalLights.assert_called_once_with(
        greenPin,
        yellowPin,
        redPin,
        blinkTime
    )

@patch('moduleLoader.Camera')
def test_setup_camera_disabled(mock_camera, xboxLoader):
    camera = xboxLoader.setup_camera("camera_disabled")

    assert camera is None
    mock_camera.assert_not_called()

@patch('moduleLoader.Camera')
def test_setup_camera_enabled(mock_camera, xboxLoader):
    xboxLoader.setup_camera("camera_enabled")

    resolution = (800, 1000)

    mock_camera.assert_called_once_with(resolution)

@patch('moduleLoader.CameraHandler')
def test_setup_camera_handling_disabled(mock_cameraHandling, xboxLoader):
    cameraHandler = xboxLoader.setup_camera_handler("camera_disabled")

    assert cameraHandler is None
    mock_cameraHandling.assert_not_called()

@patch('moduleLoader.CameraHandler')
def test_setup_camera_handling_enabled(mock_cameraHandling, xboxLoader):
    xboxLoader.setup_camera_handler("camera_enabled")

    maxZoomValue = 8.7
    zoomStep = 0.2

    mock_cameraHandling.assert_called_once_with(
        ANY,
        ANY,
        maxZoomValue,
        zoomStep
    )

@patch('moduleLoader.HonkHandling')
def test_setup_honk_handling_disabled(mock_honkHandling, audioLoader):
    honkHandler = audioLoader.setup_honk_handling("honk_disabled")

    assert honkHandler is None
    mock_honkHandling.assert_not_called()

@patch('moduleLoader.HonkHandling')
def test_setup_honk_handling_enabled(mock_honkHandling, audioLoader):
    audioLoader.setup_honk_handling("honk_enabled")

    pin = 37
    defaultHonkTime = 1.1

    mock_honkHandling.assert_called_once_with(
        pin,
        defaultHonkTime,
        ANY,
        ANY
    )

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
