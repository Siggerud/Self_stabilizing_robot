import yaml

from audioHandler import AudioHandler
from camera import Camera
from cameraHandler import CameraHandler
from cameraHelper import CameraHelper
from cameraServoHandling import CameraServoHandling
from carHandling import CarHandling
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from commandHandler import CommandHandler
from exceptions import OutOfRangeException, YamlParseException, InvalidCommandException, MicrophoneException, \
    MotionTrackingDeviceException, InvalidPinException, XboxControlException
from honkHandling import HonkHandling
from hardware.motionTrackingDevice import MotionTrackingDevice
from hardware.motorDriver import MotorDriver
from hardware.pca9685 import PCA9685
from commandGenerator import CommandGenerator
from utility.roboCarHelper import get_full_file_path
from hardware.servo import Servo
from signalLights import SignalLights
from stabilizer import Stabilizer
from commandMapperBase import CommandMapperBase
from xBoxCommandMapper import XBoxCommandMapper
from voiceCommandMapper import VoiceCommandMapper
from xBoxEventHandler import XBoxEventHandler
from xboxControl import XboxControl

class ModuleLoader:
    def __init__(self):
        self._commandMapper: CommandMapperBase = self._set_handler()

    def setup_command_generator(self) -> CommandGenerator:
        configFile: str = 'config/global.yml'
        globalSpecs: dict = self._get_yaml_contents(configFile)

        userController: str = globalSpecs["user_controller"]

        if userController == "xbox":
            return self._setup_xbox_handler()
        elif userController == "audio":
            return self._setup_audio_handler()

    def setup_command_handler(self, camera: Camera) -> CommandHandler:
        # setup car
        car = self.setup_car()

        # define servos aboard car
        servo = self.setup_servo()

        # setup honk
        honk = self.setup_honk_handling()

        # enable objects in camera class
        camera.set_car_enabled()
        camera.set_servo_enabled()

        # setup camera handler
        cameraHandler = self.setup_camera_handler()

        # setup camera helper
        cameraHelper = CameraHelper(cameraHandler, car, servo)

        cameraHelper.set_array_dict(camera.array_dict)

        # setup signal lights
        signalLights = self.setup_signal_lights()

        configFile: str = 'config/global.yml'
        globalSpecs = self._get_yaml_contents(configFile)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)

        try:
            # set up command handler
            commandHandler = CommandHandler([car, servo, cameraHandler, honk], cameraHelper, signalLights, exitCommand)
        except (InvalidCommandException, InvalidPinException) as e:
            raise YamlParseException("Error while setting up command handler") from e

        return commandHandler

    def setup_stabilizer(self):
        configFile: str = 'config/stabilizer.yml'
        stabilizerSpecs: dict = self._get_yaml_contents(configFile)

        axes = stabilizerSpecs["Axes"]
        rollAxis: str = axes["roll_axis"]
        pitchAxis: str = axes["pitch_axis"]

        offsets = stabilizerSpecs["Offset"]
        tresholds = stabilizerSpecs["Thresholds"]

        try:
            # TODO: make tests for these
            offsetX: float = float(offsets["offset_x"]) if offsets["offset_x"] is not None else 0
            offsetY: float = float(offsets["offset_y"]) if offsets["offset_y"] is not None else 0
            stabilizeOnStartup: bool = bool(offsets["set_offset_on_startup"])

            rollTreshold: int = int(tresholds["roll"])
            pitchTreshold: int = int(tresholds["pitch"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        offsets: dict[str: float] = {
            "x": offsetX,
            "y": offsetY
        }

        stabilizerServoChannels = stabilizerSpecs["Servo_channels"]

        try:
            stabilizerChannels: dict[str: int] = {
                "frontRight": int(stabilizerServoChannels["front_right"]),
                "frontLeft": int(stabilizerServoChannels["front_left"]),
                "rearLeft": int(stabilizerServoChannels["rear_left"]),
                "rearRight": int(stabilizerServoChannels["rear_right"])
            }
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            motionTrackingDevice = MotionTrackingDevice(
                rollAxis,
                pitchAxis,
                offsets,
                stabilizeOnStartup
            )
        except (MotionTrackingDeviceException, OutOfRangeException) as e:
            raise YamlParseException(f"Error while setting up motion tracking device") from e

        pca9685 = PCA9685()

        return Stabilizer(motionTrackingDevice, pca9685, rollTreshold, pitchTreshold, stabilizerChannels)

    def setup_car(self) -> CarHandling:
        configFile: str = 'config/car_handling.yml'
        carHandlingSpecs: dict = self._get_yaml_contents(configFile)

        pins = carHandlingSpecs["Pins"]
        pwm = carHandlingSpecs["PWM"]
        motorSides = carHandlingSpecs["Motors"]["Sides"]
        motorDirections = carHandlingSpecs["Motors"]["Reverse_directions"]

        motorDriverPins: dict[str: int] = {}
        motors: dict[str: str] = {"Sides": {},
                                  "ReverseDirection": {}}
        pwmValues: dict[str: int] = {}
        try:
            # define GPIO pins
            motorDriverPins["IN1"] = int(pins["IN1"])
            motorDriverPins["IN2"] = int(pins["IN2"])
            motorDriverPins["IN3"] = int(pins["IN3"])
            motorDriverPins["IN4"] = int(pins["IN4"])
            motorDriverPins["ENA"] = int(pins["ENA"])
            motorDriverPins["ENB"] = int(pins["ENB"])

            motors["Sides"]["MotorA"] = motorSides["motor_A"]
            motors["Sides"]["MotorB"] = motorSides["motor_B"]

            motors["ReverseDirection"]["MotorA"] = bool(motorDirections["motor_A"])
            motors["ReverseDirection"]["MotorB"] = bool(motorDirections["motor_B"])

            # define pwm values
            pwmValues["Minimum"] = int(pwm["minimum_motor_PWM"])
            pwmValues["Maximum"] = int(pwm["maximum_motor_PWM"])

            speedIncrement: int = int(carHandlingSpecs["Other"]["speed_step"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        # define car commands
        try:
            commandsToInstructions = self._commandMapper.get_car_handling_commands(carHandlingSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up car handling") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(carHandlingSpecs)
        try:
            motorDriver: MotorDriver = MotorDriver(
                motorDriverPins,
                motors,
                pwmValues
            )
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            # define car handling
            car = CarHandling(
                motorDriver,
                speedIncrement,
                commandsToInstructions,
                commandsToDescriptions
            )
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFile}") from e

        return car

    def _setup_xbox_handler(self) -> XBoxEventHandler:
        configFile: str = 'config/global.yml'
        globalSpecs = self._get_yaml_contents(configFile)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)
        xboxControl = XboxControl()

        try:
            xboxEventHandler = XBoxEventHandler(xboxControl, exitCommand)
        except XboxControlException:
            raise YamlParseException("Error while setting up audio handler") from e

        return xboxEventHandler

    def _setup_audio_handler(self) -> AudioHandler:
        configFile: str = 'config/audio.yml'
        audioSpecs = self._get_yaml_contents(configFile)

        language: str = audioSpecs["audio"]["language"]
        microphoneName: str = audioSpecs["audio"]["microphone_name"]

        configFile: str = 'config/global.yml'
        globalSpecs = self._get_yaml_contents(configFile)

        exitCommand: str = self._commandMapper.get_exit_command(globalSpecs)
        # TODO: make a generic error message?
        try:
            audioHandler = AudioHandler(exitCommand, language, microphoneName)
        except MicrophoneException as e:
            raise YamlParseException("Error while setting up audio handler") from e

        return audioHandler

    def setup_servo(self) -> CameraServoHandling:
        configFile: str = 'config/servo.yml'
        cameraServoSpecs = self._get_yaml_contents(configFile)

        pins = cameraServoSpecs["Pins"]
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
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

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
            raise YamlParseException(f"Values out of range for config file: {configFile}") from e

        return cameraServoHandling

    def setup_honk_handling(self) -> HonkHandling:
        configFile: str = 'config/honk.yml'
        honkSpecs: dict = self._get_yaml_contents(configFile)

        try:
            pin: int = int(honkSpecs["Pin"]["pin"])
            defaultHonkTime: float = float(honkSpecs["Honk_times"]["default_honk_time"])
            maxHonkTime: float = float(honkSpecs["Honk_times"]["max_honk_time"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e


        try:
            commandsToInstructions = self._commandMapper.get_honk_commands(honkSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up honk handling") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(honkSpecs)

        try:
            honk_handler = HonkHandling(pin, defaultHonkTime, maxHonkTime, commandsToInstructions,
                                        commandsToDescriptions)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFile}") from e

        return honk_handler

    def setup_camera_handler(self) -> CameraHandler:
        configFile: str = 'config/camera.yml'
        cameraSpecs = self._get_yaml_contents(configFile)

        zoomSpecs = cameraSpecs["zoom"]

        try:
            maxZoomValue = float(zoomSpecs["max_zoom_value"])
            zoomIncrement = float(zoomSpecs["zoom_step"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            commandsToInstructions: dict[str: CameraHelperCommand] = self._commandMapper.get_camera_helper_commands(cameraSpecs)
        except InvalidCommandException as e:
            raise YamlParseException(f"Command exception occured when setting up camera helper") from e

        commandsToDescriptions: dict[str: str] = self._commandMapper.get_command_descriptions(cameraSpecs)

        try:
            cameraHelper = CameraHandler(commandsToInstructions, commandsToDescriptions, maxZoomValue, zoomIncrement)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFile}") from e

        return cameraHelper

    def setup_camera(self) -> Camera:
        configFile: str = 'config/camera.yml'
        cameraSpecs = self._get_yaml_contents(configFile)

        resolution = cameraSpecs["Resolution"]

        try:
            resolutionWidth: int = int(resolution["width"])
            resolutionHeight: int = int(resolution["height"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        resolution: tuple = (resolutionWidth, resolutionHeight)
        camera = Camera(resolution)

        return camera

    def setup_signal_lights(self) -> SignalLights:
        configFile: str = 'config/signal_lights.yml'
        signalLightSpecs: dict = self._get_yaml_contents(configFile)

        pins: dict = signalLightSpecs["Pins"]

        try:
            greenLightPin: int = int(pins["green_pin"])
            yellowLightPin: int = int(pins["yellow_pin"])
            redLightPin: int = int(pins["red_pin"])

            blinkTime: float = float(signalLightSpecs["Other"]["blink_time"])
        except ValueError as e:
            raise YamlParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
        except OutOfRangeException as e:
            raise YamlParseException(f"Values out of range for config file: {configFile}") from e

        return signalLights

    def _set_handler(self) -> CommandMapperBase:
        configFile: str = 'config/global.yml'
        globalSpecs: dict = self._get_yaml_contents(configFile)

        userController: str = globalSpecs["user_controller"]
        validControllers: list[str] = ["xbox", "audio"]
        if userController not in validControllers:
            raise YamlParseException(f"User controller needs to be in {str(validControllers)}")

        if userController == "xbox":
            return XBoxCommandMapper()
        elif userController == "audio":
            return VoiceCommandMapper()

    def _get_yaml_contents(self, fileName: str) -> dict:
        filePath: str = get_full_file_path(fileName)
        with open(filePath, 'r') as stream:
            return yaml.safe_load(stream)
