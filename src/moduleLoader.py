from configparser import ConfigParser
import yaml
from os import path
from signalLights import SignalLights
from camera import Camera
from cameraHelper import CameraHelper
from honkHandling import HonkHandling
from cameraServoHandling import CameraServoHandling
from audioHandler import AudioHandler
from servo import Servo
from carHandling import CarHandling
from motorDriver import MotorDriver
from motionTrackingDevice import MotionTrackingDevice
from stabilizer import Stabilizer
from commandHandler import CommandHandler
from voiceCommandHandler import VoiceCommandHandler
from exceptions import OutOfRangeException, ConfigParseException, InvalidCommandException, MicrophoneException, MotionTrackingDeviceException, InvalidPinException

class ModuleLoader:
    def __init__(self):
        # set up parser
        self._parser = ConfigParser()
        self._handler = VoiceCommandHandler()

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

        # setup camerahelper
        cameraHelper = self.setup_camera_helper(car, servo)
        cameraHelper.set_array_dict(camera.array_dict)

        # setup signal lights
        signalLights = self.setup_signal_lights()

        configFile: str = 'config/global.yml'
        globalSpecs = self._get_yaml_contents(configFile)

        exitCommand: str = globalSpecs["Commands"]["exit"]

        try:
            # set up command handler
            commandHandler = CommandHandler(car, servo, cameraHelper, honk, signalLights, exitCommand)
        except (InvalidCommandException, InvalidPinException) as e:
            raise ConfigParseException("Error while setting up command handler") from e

        return commandHandler

    def setup_stabilizer(self):
        configFile: str = "stabilizer"
        self._read_config_file(self._parser, configFile)

        axes = self._parser["Axes"]
        rollAxis: str = axes["roll_axis"]
        pitchAxis: str = axes["pitch_axis"]

        offsets = self._parser["Offsets"]
        tresholds = self._parser["Tresholds"]

        try:
            offsetX: float = offsets.getfloat("offset_x")
            offsetY: float = offsets.getfloat("offset_y")
            rollTreshold: int = tresholds.getint("roll_treshold")
            pitchTreshold: int = tresholds.getint("pitch_treshold")
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        offsets: dict[str: float] = {
            "x": offsetX,
            "y": offsetY
        }

        stabilizerServoChannels = self._parser["Servo.channels"]

        try:
            stabilizerChannels: dict[str: int] = {
                "frontRight": stabilizerServoChannels.getint("front_right"),
                "frontLeft": stabilizerServoChannels.getint("front_left"),
                "rearLeft": stabilizerServoChannels.getint("rear_left"),
                "rearRight": stabilizerServoChannels.getint("rear_right")
            }
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            motionTrackingDevice = MotionTrackingDevice(rollAxis, pitchAxis, offsets)
        except MotionTrackingDeviceException as e:
            raise ConfigParseException(f"Error while setting up motion tracking device") from e

        return Stabilizer(motionTrackingDevice, rollTreshold, pitchTreshold, stabilizerChannels)

    def setup_car(self) -> CarHandling:
        configFile: str = 'config/car_handling.yml'
        carHandlingSpecs: dict = self._get_yaml_contents(configFile)

        pins = carHandlingSpecs["Pins"]
        pwm = carHandlingSpecs["PWM"]

        try:
            # define GPIO pins
            rightForward: int = int(pins["right_forward"])
            rightBackward: int = int(pins["right_backward"])
            leftForward: int = int(pins["left_forward"])
            leftBackward: int = int(pins["left_backward"])
            enA: int = int(pins["enA"])
            enB: int = int(pins["enB"])

            # define pwm values
            minPwm: int = int(pwm["minimum_motor_PWM"])
            maxPwm: int = int(pwm["maximum_motor_PWM"])

            speedStep: int = int(carHandlingSpecs["Other"]["speed_step"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        # define car commands
        carHandlingCommands: dict[str: str] = carHandlingSpecs["Commands"]

        try:
            commands = self._handler.get_car_handling_commands(carHandlingCommands, speedStep, minPwm, maxPwm)
        except InvalidCommandException as e:
            raise ConfigParseException(f"Command exception occured when setting up car handling") from e

        motorDriver: MotorDriver = MotorDriver(
            leftBackward,
            leftForward,
            rightBackward,
            rightForward,
            enA,
            enB
        )

        try:
            # define car handling
            car = CarHandling(
                motorDriver,
                minPwm,
                maxPwm,
                speedStep,
                commands
            )
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return car

    def setup_audio_handler(self) -> AudioHandler:
        configFile: str = 'config/audio.yml'
        audioSpecs = self._get_yaml_contents(configFile)

        language: str = audioSpecs["audio"]["language"]
        microphoneName: str = audioSpecs["audio"]["microphone_name"]

        configFile: str = 'config/global.yml'
        globalSpecs = self._get_yaml_contents(configFile)

        exitCommand: str = globalSpecs["Commands"]["exit"]
        #TODO: make a generic error message?
        try:
            audioHandler = AudioHandler(exitCommand, language, microphoneName)
        except MicrophoneException as e:
            raise ConfigParseException("Error while setting up audio handler") from e

        return audioHandler

    def setup_servo(self) -> CameraServoHandling:
        configFile: str = 'config/servo.yml'
        cameraServoSpecs = self._get_yaml_contents(configFile)

        pins = cameraServoSpecs["Pins"]
        angleLimitsHorizontal = cameraServoSpecs["Angle_limits_horizontal"]
        angleLimitsVertical = cameraServoSpecs["Angle_limits_vertical"]

        try:
            servoPinHorizontal: int = int(pins["servo_pin_horizontal"])
            servoPinVertical: int = int(pins["servo_pin_vertical"])

            minAngleHorizontal: int = int(angleLimitsHorizontal["min_angle"])
            maxAngleHorizontal: int = int(angleLimitsHorizontal["max_angle"])

            minAngleVertical: int = int(angleLimitsVertical["min_angle"])
            maxAngleVertical: int = int(angleLimitsVertical["max_angle"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        servoCommands = cameraServoSpecs["Commands"]

        minAngles: dict[str: int] = {
            "horizontal": minAngleHorizontal,
            "vertical": minAngleVertical
        }

        maxAngles: dict[str: int] = {
            "horizontal": maxAngleHorizontal,
            "vertical": maxAngleVertical
        }

        try:
            commands = self._handler.get_camera_servo_handling_commands(servoCommands, minAngles, maxAngles)
        except InvalidCommandException as e:
            raise ConfigParseException(f"Command exception occured when setting up honk handling") from e

        horizontalServo: Servo = Servo(servoPinHorizontal)
        verticalServo: Servo = Servo(servoPinVertical)

        try:
            cameraServoHandling = CameraServoHandling(
                horizontalServo,
                verticalServo,
                minAngles,
                maxAngles,
                commands
            )
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return cameraServoHandling

    def setup_honk_handling(self) -> HonkHandling:
        configFile: str = 'config/honk.yml'
        honkSpecs: dict = self._get_yaml_contents(configFile)

        try:
            pin: int = int(honkSpecs["Pin"]["pin"])
            defaultHonkTime: float = float(honkSpecs["Honk_times"]["default_honk_time"])
            maxHonkTime: float = float(honkSpecs["Honk_times"]["max_honk_time"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        commands: dict = honkSpecs["Commands"]

        try:
            commands = self._handler.get_honk_commands(commands, maxHonkTime)
        except InvalidCommandException as e:
            raise ConfigParseException(f"Command exception occured when setting up honk handling") from e

        try:
            honk_handler = HonkHandling(pin, defaultHonkTime, maxHonkTime, commands)
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return honk_handler

    def setup_camera_helper(self, *args) -> CameraHelper:
        configFile: str = 'config/camera.yml'
        cameraSpecs = self._get_yaml_contents(configFile)

        zoomSpecs = cameraSpecs["Zoom"]

        try:
            maxZoomValue = float(zoomSpecs["max_zoom_value"])
            zoomIncrement = float(zoomSpecs["zoom_step"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        commands = cameraSpecs["Commands"]
        try:
            commands = self._handler.get_camera_helper_commands(commands, 1.0, maxZoomValue, zoomIncrement)
        except InvalidCommandException as e:
            raise ConfigParseException(f"Command exception occured when setting up camera helper") from e

        try:
            cameraHelper = CameraHelper(commands, maxZoomValue, zoomIncrement, *args)
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return cameraHelper

    def setup_camera(self) -> Camera:
        configFile: str = 'config/camera.yml'
        cameraSpecs = self._get_yaml_contents(configFile)

        resolution = cameraSpecs["Resolution"]

        try:
            resolutionWidth: int = int(resolution["width"])
            resolutionHeight: int = int(resolution["height"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

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
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return signalLights

    def _get_full_file_path(self, filePath: str) -> str:
        return path.join(path.dirname(__file__), filePath)

    def _get_yaml_contents(self, fileName: str) -> dict:
        filePath: str = self._get_full_file_path(fileName)
        with open(filePath, 'r') as stream:
            return yaml.safe_load(stream)

    def _read_config_file(self, parser, fileName):
        parser.read(path.join(path.dirname(__file__), 'config/' + fileName + ".ini"))