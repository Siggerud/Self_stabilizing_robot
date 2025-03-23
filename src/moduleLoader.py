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

        self._read_config_file(self._parser, "global")
        exitCommand = self._parser["Commands"]["exit"]

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
        configFile: str = "car_handling"
        self._read_config_file(self._parser, configFile)
        pins = self._parser["Pins"]
        pwm = self._parser["PWM"]

        try:
            # define GPIO pins
            rightForward: int = pins.getint("right_forward")
            rightBackward: int = pins.getint("right_backward")
            leftForward: int = pins.getint("left_forward")
            leftBackward: int = pins.getint("left_backward")
            enA: int = pins.getint("enA")
            enB: int = pins.getint("enB")

            # define pwm values
            minPwm: int = pwm.getint("minimum_motor_PWM")
            maxPwm: int = pwm.getint("maximum_motor_PWM")

            speedStep: int = self._parser["Other"].getint("speed_step")
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        # define car commands
        carHandlingCommands = self._parser["Commands"]

        handler = VoiceCommandHandler()

        try:
            commands = handler.get_car_handling_commands(carHandlingCommands, speedStep, minPwm, maxPwm)
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
        filePath: str = self._get_full_file_path('config/audio.yml')
        with open(filePath, 'r') as stream:
            audioSpecs = yaml.safe_load(stream)

        language: str = audioSpecs["audio"]["language"]
        microphoneName: str = audioSpecs["audio"]["microphone_name"]

        self._read_config_file(self._parser, "global")

        exitCommand: str = self._parser["Commands"]["exit"]
        #TODO: make a generic error message?
        try:
            audioHandler = AudioHandler(exitCommand, language, microphoneName)
        except MicrophoneException as e:
            raise ConfigParseException("Error while setting up audio handler") from e

        return audioHandler

    def setup_servo(self) -> CameraServoHandling:
        configFile: str = "servo"
        self._read_config_file(self._parser, configFile)
        pins = self._parser["Pins"]
        angleLimitsHorizontal = self._parser["Angle_limits_horizontal"]
        angleLimitsVertical = self._parser["Angle_limits_vertical"]

        try:
            servoPinHorizontal: int = pins.getint("servo_pin_horizontal")
            servoPinVertical: int = pins.getint("servo_pin_vertical")

            minAngleHorizontal: int = angleLimitsHorizontal.getint("min_angle")
            maxAngleHorizontal: int = angleLimitsHorizontal.getint("max_angle")

            minAngleVertical: int = angleLimitsVertical.getint("min_angle")
            maxAngleVertical: int = angleLimitsVertical.getint("max_angle")
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        servoCommands = self._parser["Commands"]

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
        configFile: str = "honk"
        self._read_config_file(self._parser, "honk")
        honkTimes = self._parser["Honk.times"]

        try:
            pin: int = self._parser["Pin"].getint("pin")
            defaultHonkTime: float = honkTimes.getfloat("default_honk_time")
            maxHonkTime: float = honkTimes.getfloat("max_honk_time")
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        commands = self._parser["Commands"]

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
        configFile: str = "camera"
        self._read_config_file(self._parser, configFile)
        commands = self._parser["Commands"]

        zoomSpecs = self._parser["Zoom"]

        try:
            maxZoomValue = float(zoomSpecs["max_zoom_value"])
            zoomIncrement = float(zoomSpecs["zoom_step"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

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
        filePath: str = self._get_full_file_path(configFile)
        with open(filePath, 'r') as stream:
            cameraSpecs = yaml.safe_load(stream)

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
        configFile: str = "signal_lights"
        self._read_config_file(self._parser, configFile)
        pins = self._parser["Pins"]
        other = self._parser["Other"]

        try:
            greenLightPin: int = pins.getint("green_pin")
            yellowLightPin: int = pins.getint("yellow_pin")
            redLightPin: int = pins.getint("red_pin")

            blinkTime: float = float(other["blink_time"])
        except ValueError as e:
            raise ConfigParseException(f"Error while unpacking config file: {configFile}") from e

        try:
            signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
        except OutOfRangeException as e:
            raise ConfigParseException(f"Values out of range for config file: {configFile}") from e

        return signalLights

    def _get_full_file_path(self, filePath: str) -> str:
        return path.join(path.dirname(__file__), filePath)

    def _read_config_file(self, parser, fileName):
        parser.read(path.join(path.dirname(__file__), 'config/' + fileName + ".ini"))