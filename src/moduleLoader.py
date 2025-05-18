from typing import Optional

from motionTrackingDevice import MotionTrackingDevice
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
from exceptions import OutOfRangeException, YamlParseException, InvalidCommandException, MicrophoneException, \
    InvalidPinException, XboxControlException
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

        try:
            # set up command handler
            commandHandler = CommandHandler(commandExecutors, cameraHelper, signalLights, exitCommand)
        except (InvalidCommandException, InvalidPinException) as e:
            raise YamlParseException("Error while setting up command handler") from e

        return commandHandler

    def _setup_camera_helper(self, cameraHandler, car, servo, camera) -> Optional[CameraHelper]:
        if camera is None:
            return None
        return CameraHelper(camera.array_dict, cameraHandler, car, servo, )

    def setup_stabilizer(self, configFileName: str) -> Optional[Stabilizer]:
        stabilizerSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(stabilizerSpecs, configFileName):
            return None

        motionTrackingDevice = self._setup_motion_tracking_device(stabilizerSpecs)

        tresholds: dict = stabilizerSpecs["thresholds"]

        offsetX: float = get_float(offsets, "offset_x") if offsets["offset_x"] is not None else 0
        offsetY: float = get_float(offsets, "offset_y") if offsets["offset_y"] is not None else 0

        offsets: dict[str: float] = {
            "x": offsetX,
            "y": offsetY
        }

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
        if not self._check_if_module_enabled(carHandlingSpecs, configFileName):
            return None

        motorDriver = self._setup_motor_driver(carHandlingSpecs)

        speedIncrement: int = get_int(carHandlingSpecs["other"], "speed_step")

        # define car commands
        commandsToInstructions = self._commandMapper.get_car_handling_commands(carHandlingSpecs)
        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(carHandlingSpecs)

        # define car handling
        car = CarHandling(
            motorDriver,
            speedIncrement,
            commandsToInstructions,
            commandsToDescriptions
        )

        return car

    def _setup_motion_tracking_device(self, stabilizerSpecs: dict) -> MotionTrackingDevice:
        axes: dict = stabilizerSpecs["axes"]
        rollAxis: str = axes["roll_axis"]
        pitchAxis: str = axes["pitch_axis"]

        offsets: dict = stabilizerSpecs["offset"]

        stabilizeOnStartup: bool = get_bool(offsets, "set_offset_on_startup")

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

    def _setup_xbox_handler(self) -> XBoxEventHandler:
        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)
        xboxControl = XboxControl()

        try:
            xboxEventHandler = XBoxEventHandler(xboxControl, exitCommand)
        except XboxControlException as e:
            raise YamlParseException("Error while setting up audio handler") from e

        return xboxEventHandler

    def _setup_audio_handler(self) -> AudioHandler:
        configFile: str = 'audio'
        audioSpecs: dict = self._get_content_from_config_file(configFile)

        language: str = audioSpecs["audio"]["language"]
        microphoneName: str = audioSpecs["audio"]["microphone_name"]

        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)
        # TODO: make a generic error message?
        try:
            audioHandler = AudioHandler(exitCommand, language, microphoneName)
        except MicrophoneException as e:
            raise YamlParseException("Error while setting up audio handler") from e

        return audioHandler

    def setup_servo(self, configFileName: str) -> Optional[CameraServoHandling]:
        cameraServoSpecs = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraServoSpecs, configFileName):
            return None

        pins = cameraServoSpecs["pins"]
        angleLimitsHorizontal = cameraServoSpecs["angle_limits_horizontal"]
        angleLimitsVertical = cameraServoSpecs["angle_limits_vertical"]

        try:
            servoPinHorizontal: int = int(pins["servo_pin_horizontal"])
            servoPinVertical: int = int(pins["servo_pin_vertical"])

            minAngleHorizontal: int = int(angleLimitsHorizontal["min_angle"])
            maxAngleHorizontal: int = int(angleLimitsHorizontal["max_angle"])

            minAngleVertical: int = int(angleLimitsVertical["min_angle"])
            maxAngleVertical: int = int(angleLimitsVertical["max_angle"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFileName}") from e

        minAngles: dict[str: int] = {
            "horizontal": minAngleHorizontal,
            "vertical": minAngleVertical
        }

        maxAngles: dict[str: int] = {
            "horizontal": maxAngleHorizontal,
            "vertical": maxAngleVertical
        }

        try:
            commandsToInstructions = self._commandMapper.get_camera_servo_handling_commands(cameraServoSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up honk handling") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(cameraServoSpecs)
        horizontalServo: Servo = Servo(servoPinHorizontal)
        verticalServo: Servo = Servo(servoPinVertical)

        try:
            cameraServoHandling = CameraServoHandling(
                horizontalServo,
                verticalServo,
                minAngles,
                maxAngles,
                commandsToInstructions,
                commandsToDescriptions
            )
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFileName}") from e

        return cameraServoHandling

    def setup_honk_handling(self, configFileName: str) -> Optional[HonkHandling]:
        honkSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(honkSpecs, configFileName):
            return None

        try:
            pin: int = int(honkSpecs["pin"]["pin"])
            defaultHonkTime: float = float(honkSpecs["honk_times"]["default_honk_time"])
            maxHonkTime: float = float(honkSpecs["honk_times"]["max_honk_time"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFileName}") from e

        try:
            commandsToInstructions = self._commandMapper.get_honk_commands(honkSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up honk handling") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(honkSpecs)

        try:
            honk_handler = HonkHandling(pin, defaultHonkTime, maxHonkTime, commandsToInstructions,
                                        commandsToDescriptions)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFileName}") from e

        return honk_handler

    def setup_camera_handler(self, configFileName: str) -> Optional[CameraHandler]:
        cameraSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraSpecs, configFileName):
            return None

        zoomSpecs: dict = cameraSpecs["zoom"]

        try:
            maxZoomValue = float(zoomSpecs["max_zoom_value"])
            zoomIncrement = float(zoomSpecs["zoom_step"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFileName}") from e

        try:
            commandsToInstructions: dict[str: CameraHelperCommand] = self._commandMapper.get_camera_helper_commands(
                cameraSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up camera helper") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(cameraSpecs)

        try:
            cameraHelper = CameraHandler(commandsToInstructions, commandsToDescriptions, maxZoomValue, zoomIncrement)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFileName}") from e

        return cameraHelper

    def setup_camera(self, configFileName: str) -> Optional[Camera]:
        cameraSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(cameraSpecs, configFileName):
            return None

        resolution: set[int] = cameraSpecs["resolution"]

        try:
            resolutionWidth: int = int(resolution["width"])
            resolutionHeight: int = int(resolution["height"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFileName}") from e

        resolution: tuple = (resolutionWidth, resolutionHeight)
        camera = Camera(resolution)

        return camera

    def setup_signal_lights(self, configFileName: str) -> Optional[SignalLights]:
        signalLightSpecs: dict = self._get_content_from_config_file(configFileName)

        if not self._check_if_module_enabled(signalLightSpecs, configFileName):
            return None

        pins: dict = signalLightSpecs["pins"]

        try:
            greenLightPin: int = int(pins["green_pin"])
            yellowLightPin: int = int(pins["yellow_pin"])
            redLightPin: int = int(pins["red_pin"])

            blinkTime: float = float(signalLightSpecs["other"]["blink_time"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFileName}") from e

        try:
            signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFileName}") from e

        return signalLights

    def _set_handler(self) -> CommandMapperBase:
        globalSpecs: dict = self._get_content_from_config_file(self._globalConfigFileName)

        userController: str = globalSpecs["user_controller"]
        validControllers: list[str] = ["xbox", "audio"]
        if userController not in validControllers:
            raise YamlParseException(f"User controller needs to be in {str(validControllers)}")

        if userController == "xbox":
            return XBoxCommandMapper()
        elif userController == "audio":
            return VoiceCommandMapper()

    def _get_content_from_config_file(self, configFileName: str) -> dict:
        absoluteFilePath: str = path.join(self._configDirPath, configFileName + '.yml')

        return get_yaml_content_from_file(absoluteFilePath)

    def _check_if_module_enabled(self, specs: dict, configFile: str) -> bool:
        try:
            enabled = bool(specs["enabled"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        return enabled


