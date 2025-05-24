from typing import Optional

from utility.yamlParser import get_yaml_content_from_file, get_float, get_int, get_bool
from audioHandler import AudioHandler
from camera import Camera
from cameraHandler import CameraHandler
from cameraHelper import CameraHelper
from cameraServoHandling import CameraServoHandling
from carHandling import CarHandling
from commandGenerator import CommandGenerator
from commandHandler import CommandHandler
from commandMapperBase import CommandMapperBase
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from exceptions import YamlParseException
from hardware.motionTrackingDevice import MotionTrackingDevice
from hardware.motorDriver import MotorDriver
from hardware.pca9685 import PCA9685
from hardware.servo import Servo
from honkHandling import HonkHandling
from signalLights import SignalLights
from stabilizer import Stabilizer
from os import path
from voiceCommandMapper import VoiceCommandMapper
from xBoxCommandMapper import XBoxCommandMapper
from xBoxEventHandler import XBoxEventHandler
from xboxControl import XboxControl
from keyboardEventHandler import KeyboardEventHandler
from keyboardMapper import KeyboardMapper

class ModuleLoader:
    def __init__(self, configDirPath: str, globalConfigFileName: str):
        self._configDirPath = configDirPath
        self._globalConfigFileName = globalConfigFileName
        self._commandMapper: CommandMapperBase = self._set_handler()

    def setup_command_generator(self) -> CommandGenerator:
        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        userController: str = globalSpecs["user_controller"]

        if userController == "xbox":
            return self._setup_xbox_handler()
        elif userController == "audio":
            return self._setup_audio_handler()
        elif userController == "keyboard":
            return self._setup_keyboard_handler()

    def setup_command_handler(self, camera: Optional[Camera], car: Optional[CarHandling],
                              servo: Optional[CameraServoHandling], cameraHandler: Optional[CameraHandler],
                              honk: Optional[HonkHandling], signalLights: Optional[SignalLights]) -> Optional[CommandHandler]:
        if camera is not None:
            # enable objects in camera class
            camera.set_car_enabled_if_exists(car)
            camera.set_servo_enabled_if_exists(servo)

        commandExecutors: list = [executor for executor in [car, servo, cameraHandler, honk] if executor is not None]
        if len(commandExecutors) == 0: # no objects to receive commands
            return None

        # setup camera helper
        cameraHelper = self._setup_camera_helper(cameraHandler, car, servo, camera)

        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)

        # set up command handler
        return CommandHandler(commandExecutors, cameraHelper, signalLights, exitCommand)

    def setup_camera_servo_handling(self, configFileName: str) -> Optional[CameraServoHandling]:
        cameraServoSpecs = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraServoSpecs):
            return None

        pins = cameraServoSpecs["pins"]
        angleLimitsHorizontal = cameraServoSpecs["angle_limits_horizontal"]
        angleLimitsVertical = cameraServoSpecs["angle_limits_vertical"]

        servoPinHorizontal: int = get_int(pins, "servo_pin_horizontal")
        servoPinVertical: int = get_int(pins, "servo_pin_vertical")

        minAngleHorizontal: int = get_int(angleLimitsHorizontal, "min_angle")
        maxAngleHorizontal: int = get_int(angleLimitsHorizontal, "max_angle")

        minAngleVertical: int = get_int(angleLimitsVertical, "min_angle")
        maxAngleVertical: int = get_int(angleLimitsVertical, "max_angle")

        minAngles: dict[str: int] = {
            "horizontal": minAngleHorizontal,
            "vertical": minAngleVertical
        }

        maxAngles: dict[str: int] = {
            "horizontal": maxAngleHorizontal,
            "vertical": maxAngleVertical
        }


        commandsToInstructions = self._commandMapper.get_camera_servo_handling_commands(cameraServoSpecs)
        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(cameraServoSpecs)

        horizontalServo: Servo = Servo(servoPinHorizontal)
        verticalServo: Servo = Servo(servoPinVertical)

        return CameraServoHandling(
            horizontalServo,
            verticalServo,
            minAngles,
            maxAngles,
            commandsToInstructions,
            commandsToDescriptions
        )

    def _setup_keyboard_handler(self):
        return KeyboardEventHandler()

    def setup_signal_lights(self, configFileName: str) -> Optional[SignalLights]:
        signalLightSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(signalLightSpecs):
            return None

        pins: dict = signalLightSpecs["pins"]

        greenLightPin: int = get_int(pins, "green_pin")
        yellowLightPin: int = get_int(pins, "yellow_pin")
        redLightPin: int = get_int(pins, "red_pin")

        blinkTime: float = get_float(signalLightSpecs["other"], "blink_time")

        return SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)

    def setup_camera(self, configFileName: str) -> Optional[Camera]:
        cameraSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraSpecs):
            return None

        resolutionData: dict[str: int] = cameraSpecs["resolution"]
        resolutionWidth: int = get_int(resolutionData, "width")
        resolutionHeight: int = get_int(resolutionData, "height")

        resolution: tuple = (resolutionWidth, resolutionHeight)

        return Camera(resolution)

    def setup_camera_handler(self, configFileName: str) -> Optional[CameraHandler]:
        cameraSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraSpecs):
            return None

        zoomSpecs: dict = cameraSpecs["zoom"]
        maxZoomValue = get_float(zoomSpecs, "max_zoom_value")
        zoomIncrement = get_float(zoomSpecs, "zoom_step")

        commandsToInstructions: dict[str: CameraHelperCommand] = self._commandMapper.get_camera_helper_commands(
            cameraSpecs)
        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(cameraSpecs)
        print(commandsToInstructions)
        return CameraHandler(commandsToInstructions, commandsToDescriptions, maxZoomValue, zoomIncrement)

    def setup_honk_handling(self, configFileName: str) -> Optional[HonkHandling]:
        honkSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(honkSpecs):
            return None

        pin: int = get_int(honkSpecs["pin"], "pin")
        defaultHonkTime: float = get_float(honkSpecs["honk_times"], "default_honk_time")

        commandsToInstructions = self._commandMapper.get_honk_commands(honkSpecs)
        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(honkSpecs)

        return HonkHandling(pin, defaultHonkTime, commandsToInstructions,
                                        commandsToDescriptions)

    def setup_stabilizer(self, configFileName: str) -> Optional[Stabilizer]:
        stabilizerSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(stabilizerSpecs):
            return None

        motionTrackingDevice = self._setup_motion_tracking_device(stabilizerSpecs)

        tresholds: dict = stabilizerSpecs["thresholds"]

        rollTreshold: int = get_int(tresholds, "roll")
        pitchTreshold: int = get_int(tresholds, "pitch")

        tresholds: dict[str: int] = {
            "roll": rollTreshold,
            "pitch": pitchTreshold
        }

        stabilizerServoChannels = stabilizerSpecs["servo_channels"]

        stabilizerChannels: dict[str: int] = {
            "frontRight": get_int(stabilizerServoChannels, "front_right"),
            "frontLeft": get_int(stabilizerServoChannels, "front_left"),
            "rearLeft": get_int(stabilizerServoChannels, "rear_left"),
            "rearRight": get_int(stabilizerServoChannels, "rear_right")
        }

        pca9685 = PCA9685()

        return Stabilizer(motionTrackingDevice, pca9685, tresholds, stabilizerChannels)

    def setup_car_handling(self, configFileName: str) -> Optional[CarHandling]:
        carHandlingSpecs: dict = self._get_content_from_config_file(configFileName)
        if not self._check_if_module_enabled(carHandlingSpecs):
            return None

        motorDriver = self._setup_motor_driver(carHandlingSpecs)

        speedIncrement: int = get_int(carHandlingSpecs["other"], "speed_step")

        # define car commands
        commandsToInstructions = self._commandMapper.get_car_handling_commands(carHandlingSpecs)
        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(carHandlingSpecs)

        # define car handling
        return CarHandling(
            motorDriver,
            speedIncrement,
            commandsToInstructions,
            commandsToDescriptions
        )

    def _setup_motion_tracking_device(self, stabilizerSpecs: dict) -> MotionTrackingDevice:
        axes: dict = stabilizerSpecs["axes"]
        rollAxis: str = axes["roll_axis"]
        pitchAxis: str = axes["pitch_axis"]

        offsetSpecs: dict = stabilizerSpecs["offset"]
        offsetX: float = get_float(offsetSpecs, "offset_x") if offsetSpecs["offset_x"] is not None else 0
        offsetY: float = get_float(offsetSpecs, "offset_y") if offsetSpecs["offset_y"] is not None else 0

        offsets: dict[str: float] = {
            "x": offsetX,
            "y": offsetY
        }

        stabilizeOnStartup: bool = get_bool(offsetSpecs, "set_offset_on_startup")

        return MotionTrackingDevice(
            rollAxis,
            pitchAxis,
            offsets,
            stabilizeOnStartup
        )

    def _setup_motor_driver(self, carHandlingSpecs: dict) -> MotorDriver:
        pins = carHandlingSpecs["pins"]
        pwm = carHandlingSpecs["pwm"]
        motorSides = carHandlingSpecs["motors"]["sides"]
        motorDirections = carHandlingSpecs["motors"]["reverse_directions"]

        motorDriverPins: dict[str: int] = {}
        motors: dict[str: str] = {"Sides": {},
                                  "ReverseDirection": {}}
        pwmValues: dict[str: int] = {}

        # define GPIO pins
        motorDriverPins["IN1"] = get_int(pins, "IN1")
        motorDriverPins["IN2"] = get_int(pins, "IN2")
        motorDriverPins["IN3"] = get_int(pins, "IN3")
        motorDriverPins["IN4"] = get_int(pins, "IN4")
        motorDriverPins["ENA"] = get_int(pins, "ENA")
        motorDriverPins["ENB"] = get_int(pins, "ENB")

        motors["Sides"]["MotorA"] = motorSides["motor_A"]
        motors["Sides"]["MotorB"] = motorSides["motor_B"]

        motors["ReverseDirection"]["MotorA"] = get_bool(motorDirections, "motor_A")
        motors["ReverseDirection"]["MotorB"] = get_bool(motorDirections, "motor_B")

        # define pwm values
        pwmValues["Minimum"] = get_int(pwm, "minimum_motor_PWM")
        pwmValues["Maximum"] = get_int(pwm, "maximum_motor_PWM")

        return MotorDriver(
            motorDriverPins,
            motors,
            pwmValues
        )

    def _setup_camera_helper(self, cameraHandler, car, servo, camera) -> Optional[CameraHelper]:
        if camera is None:
            return None
        return CameraHelper(camera.array_dict, cameraHandler, car, servo)

    def _setup_xbox_handler(self) -> XBoxEventHandler:
        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)
        xboxControl = XboxControl()

        return XBoxEventHandler(xboxControl, exitCommand)

    def _setup_audio_handler(self) -> AudioHandler:
        configFile: str = 'audio'
        audioSpecs: dict = self._get_content_from_config_file(configFile)

        language: str = audioSpecs["audio"]["language"]
        microphoneName: str = audioSpecs["audio"]["microphone_name"]

        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)

        return AudioHandler(exitCommand, language, microphoneName)

    def _set_handler(self) -> CommandMapperBase:
        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        userController: str = globalSpecs["user_controller"]
        validControllers: list[str] = ("xbox", "audio", "keyboard")
        if userController not in validControllers:
            raise YamlParseException(f"User controller needs to be in {str(validControllers)}")

        if userController == "xbox":
            return XBoxCommandMapper()
        elif userController == "audio":
            return VoiceCommandMapper()
        elif userController == "keyboard":
            return KeyboardMapper()

    def _get_content_from_config_file(self, configFileName: str) -> dict:
        absoluteFilePath: str = path.join(self._configDirPath, configFileName + '.yml')

        return get_yaml_content_from_file(absoluteFilePath)

    def _check_if_module_enabled(self, specs: dict) -> bool:
        return get_bool(specs, "enabled")



