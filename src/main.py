from carHandling import CarHandling
from camera import Camera
from cameraHelper import CameraHelper
from cameraServoHandling import CameraServoHandling
from carControl import CarControl
from commandHandler import CommandHandler
from roboCarHelper import RobocarHelper
from configparser import ConfigParser
from servo import Servo
from motorDriver import MotorDriver
from os import path
from signalLights import SignalLights
from audioHandler import AudioHandler
from honkHandling import HonkHandling
from stabilizer import Stabilizer
from motionTrackingDevice import MotionTrackingDevice
from exceptions import OutOfRangeException, X11ForwardingException, MicrophoneException, MotionTrackingDeviceException, InvalidCommandException, InvalidPinException
from voiceCommandHandler import VoiceCommandHandler

def print_error_message_and_exit(errorMessage):
    RobocarHelper.print_startup_error(errorMessage)
    exit()


def read_config_file(parser, fileName):
    parser.read(path.join(path.dirname(__file__), 'config/' + fileName + ".ini"))


def setup_signal_lights(parser):
    read_config_file(parser, "signal_lights")
    pins = parser["Pins"]
    other = parser["Other"]

    try:
        greenLightPin: int = pins.getint("green_pin")
        yellowLightPin: int = pins.getint("yellow_pin")
        redLightPin: int = pins.getint("red_pin")

        blinkTime: float = float(other["blink_time"])
    except ValueError as e:
        print_error_message_and_exit(e)

    try:
        signalLights = SignalLights(greenLightPin, yellowLightPin, redLightPin, blinkTime)
    except OutOfRangeException as e:
        print_error_message_and_exit(e)

    return signalLights


def setup_camera(parser):
    read_config_file(parser, "camera")

    resolution = parser["Resolution"]

    try:
        resolutionWidth: int = resolution.getint("width")
        resolutionHeight: int = resolution.getint("height")
    except ValueError as e:
        print_error_message_and_exit(e)

    resolution: tuple = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution)

    return camera


def setup_camera_helper(parser: ConfigParser, *args):
    read_config_file(parser, "camera")
    commands = parser["Commands"]

    zoomSpecs = parser["Zoom"]

    try:
        maxZoomValue = float(zoomSpecs["max_zoom_value"])
        zoomIncrement = float(zoomSpecs["zoom_step"])
    except ValueError as e:
        print_error_message_and_exit(e)

    handler = VoiceCommandHandler()
    commands = handler.get_camera_helper_commands(commands, 1.0, maxZoomValue, zoomIncrement)

    try:
        cameraHelper = CameraHelper(commands, maxZoomValue, zoomIncrement, *args)
    except OutOfRangeException as e:
        print_error_message_and_exit(e)

    return cameraHelper


def setup_honk_handling(parser) -> HonkHandling:
    read_config_file(parser, "honk")
    honkTimes = parser["Honk.times"]

    try:
        pin: int = parser["Pin"].getint("pin")
        defaultHonkTime: float = honkTimes.getfloat("default_honk_time")
        maxHonkTime: float = honkTimes.getfloat("max_honk_time")
    except ValueError as e:
        print_error_message_and_exit(e)

    commands = parser["Commands"]

    handler = VoiceCommandHandler()
    commands = handler.get_honk_commands(commands, maxHonkTime)

    try:
        honk_handler = HonkHandling(pin, defaultHonkTime, maxHonkTime, commands)
    except OutOfRangeException as e:
        print_error_message_and_exit(e)

    return honk_handler


def setup_servo(parser):
    read_config_file(parser, "servo")
    pins = parser["Pins"]
    angleLimitsHorizontal = parser["Angle_limits_horizontal"]
    angleLimitsVertical = parser["Angle_limits_vertical"]

    try:
        servoPinHorizontal: int = pins.getint("servo_pin_horizontal")
        servoPinVertical: int = pins.getint("servo_pin_vertical")

        minAngleHorizontal: int = angleLimitsHorizontal.getint("min_angle")
        maxAngleHorizontal: int = angleLimitsHorizontal.getint("max_angle")

        minAngleVertical: int = angleLimitsVertical.getint("min_angle")
        maxAngleVertical: int = angleLimitsVertical.getint("max_angle")

    except ValueError as e:
        print_error_message_and_exit(e)

    servoCommands = parser["Commands"]

    minAngles: dict[str: int] = {
        "horizontal": minAngleHorizontal,
        "vertical": minAngleVertical
    }

    maxAngles: dict[str: int] = {
        "horizontal": maxAngleHorizontal,
        "vertical": maxAngleVertical
    }

    handler = VoiceCommandHandler()
    commands = handler.get_camera_servo_handling_commands(servoCommands, minAngles, maxAngles)

    horizontalServo: Servo = Servo(servoPinHorizontal)
    verticalServo: Servo = Servo(servoPinVertical)

    try:
        servo = CameraServoHandling(
            horizontalServo,
            verticalServo,
            minAngles,
            maxAngles,
            commands
        )
    except OutOfRangeException as e:
        print_error_message_and_exit(e)

    return servo


def setup_audio_handler(parser):
    read_config_file(parser, "audio")
    audioSpecs = parser["Audio"]

    language: str = audioSpecs["language"]
    microphoneName: str = audioSpecs["microphone_name"]

    read_config_file(parser, "global")

    exitCommand: str = parser["Commands"]["exit"]

    try:
        audioHandler = AudioHandler(exitCommand, language, microphoneName)
    except MicrophoneException as e:
        print_error_message_and_exit(e)

    return audioHandler


def setup_car(parser):
    read_config_file(parser, "car_handling")
    pins = parser["Pins"]
    pwm = parser["PWM"]

    try:
        # define GPIO pins
        rightForward: int = pins.getint("right_forward")
        rightBackward: int = pins.getint("right_backward")
        leftForward: int = pins.getint("left_forward")
        leftBackward: int = pins.getint("left_backward")
        enA: int = pins.getint("enA")
        enB: int = pins.getint("enB")

        # define pwm values
        minPwmTT: int = pwm.getint("minimum_motor_PWM")
        maxPwmTT: int = pwm.getint("maximum_motor_PWM")

        speedStep: int = parser["Other"].getint("speed_step")
    except ValueError as e:
        print_error_message_and_exit(e)

    # define car commands
    carHandlingCommands = parser["Commands"]
    directionCommands: dict = {
        "turnLeftCommand": carHandlingCommands["turn_left"],
        "turnRightCommand": carHandlingCommands["turn_right"],
        "driveCommand": carHandlingCommands["drive"],
        "reverseCommand": carHandlingCommands["reverse"],
        "stopCommand": carHandlingCommands["stop"],
    }

    speedCommands: dict = {
        "increaseSpeedCommand": carHandlingCommands["increase_speed"],
        "decreaseSpeedCommand": carHandlingCommands["decrease_speed"],
        "exactSpeedCommand_param": carHandlingCommands["exact_speed"]
    }

    commands: dict[str: dict] = {
        "direction": directionCommands,
        "speed": speedCommands
    }

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
            minPwmTT,
            maxPwmTT,
            speedStep,
            commands
        )
    except OutOfRangeException as e:
        print_error_message_and_exit(e)

    return car


def setup_stabilizer(parser):
    read_config_file(parser, "stabilizer")

    axes = parser["Axes"]
    rollAxis: str = axes["roll_axis"]
    pitchAxis: str = axes["pitch_axis"]

    offsets = parser["Offsets"]
    tresholds = parser["Tresholds"]

    try:
        offsetX: float = offsets.getfloat("offset_x")
        offsetY: float = offsets.getfloat("offset_y")
        rollTreshold: int = tresholds.getint("roll_treshold")
        pitchTreshold: int = tresholds.getint("pitch_treshold")
    except ValueError as e:
        print_error_message_and_exit(e)

    offsets: dict[str: float] = {
        "x": offsetX,
        "y": offsetY
    }

    stabilizerServoChannels = parser["Servo.channels"]

    try:
        stabilizerChannels: dict[str: int] = {
            "frontRight": stabilizerServoChannels.getint("front_right"),
            "frontLeft": stabilizerServoChannels.getint("front_left"),
            "rearLeft": stabilizerServoChannels.getint("rear_left"),
            "rearRight": stabilizerServoChannels.getint("rear_right")
        }
    except ValueError as e:
        print_error_message_and_exit(e)

    try:
        motionTrackingDevice = MotionTrackingDevice(rollAxis, pitchAxis, offsets)
    except MotionTrackingDeviceException as e:
        print_error_message_and_exit(e)

    return Stabilizer(motionTrackingDevice, rollTreshold, pitchTreshold, stabilizerChannels)


def setup_command_handler(parser, camera):
    # setup car
    car = setup_car(parser)

    # define servos aboard car
    servo = setup_servo(parser)

    # setup honk
    honk = setup_honk_handling(parser)

    # enable objects in camera class
    camera.set_car_enabled()
    camera.set_servo_enabled()

    # setup camerahelper
    cameraHelper = setup_camera_helper(parser, car, servo)
    cameraHelper.set_array_dict(camera.array_dict)

    # setup signal lights
    signalLights = setup_signal_lights(parser)

    read_config_file(parser, "global")
    exitCommand = parser["Commands"]["exit"]

    try:
        # set up command handler
        commandHandler = CommandHandler(car, servo, cameraHelper, honk, signalLights, exitCommand)
    except (InvalidCommandException, InvalidPinException) as e:
        print_error_message_and_exit()

    return commandHandler


if __name__ == "__main__":
    # set up parser
    parser = ConfigParser()

    # setup camera
    camera = setup_camera(parser)

    # setup command handler
    commandHandler = setup_command_handler(parser, camera)

    audioHandler = setup_audio_handler(parser)
    audioHandler.setup(commandHandler.pipeSender)

    stabilizer = setup_stabilizer(parser)

    # setup car controller
    try:
        carController = CarControl(camera, commandHandler, audioHandler, stabilizer)
    except X11ForwardingException as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()
