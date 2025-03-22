from commandContainers.cameraServoCommand import CameraServoCommand
from commandExecutors import CommandExecutors
from roboCarHelper import RobocarHelper
from servo import Servo

class CameraServoHandling(CommandExecutors):
    def __init__(self, horizontalServo: Servo, verticalServo: Servo, minAngles: list[int], maxAngles: list[int], userCommands: dict):
        self._check_argument_validity(minAngles, maxAngles)

        self._userCommands: dict[str: CameraServoCommand] = userCommands
        self._minAngles: dict[str: int] = minAngles
        self._maxAngles: dict[str: int] = maxAngles

        self._servos: dict = {
            "horizontal": horizontalServo,
            "vertical": verticalServo
        }

        self._neutralAngle: int = 0

    @property
    def pins(self) -> list[int]:
        return [self._servos["horizontal"].servoPin, self._servos["vertical"].servoPin]

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    def setup(self) -> None:
        for servo in list(self._servos.values()):
            servo.setup()

        self._center_servo_positions()

    def handle_command(self, command: str) -> None:
        commandInstructions: CameraServoCommand = self._userCommands[command]
        if commandInstructions.verticalAngle is not None and commandInstructions.horizontalAngle is not None:
            self._move_servo("vertical", commandInstructions.verticalAngle)
            self._move_servo("horizontal", commandInstructions.horizontalAngle)
        elif commandInstructions.horizontalAngle is not None:
            self._move_servo("horizontal", commandInstructions.horizontalAngle)
        elif commandInstructions.verticalAngle is not None:
            self._move_servo("vertical", commandInstructions.verticalAngle)

    def get_current_servo_angle(self, plane) -> int:
        return self._servos[plane].current_angle

    def cleanup(self) -> None:
        self._center_servo_positions()  # center camera when exiting
        for servo in list(self._servos.values()):
            servo.cleanup()

    def print_commands(self) -> None:
        # allDictsWithCommands: dict = {}
        # allDictsWithCommands.update(self._lookOffsetCommands)
        # allDictsWithCommands.update(self._lookCenterCommand)
        # allDictsWithCommands.update(self._variableCommands)
        # title: str = "Servo handling commands:"
        #
        # RobocarHelper.print_commands(title, allDictsWithCommands)
        pass

    def get_command_validity(self, command: str) -> str:
        # check if angles stay unchanged
        commandInstructions: CameraServoCommand = self._userCommands[command]
        if commandInstructions.verticalAngle is not None and commandInstructions.horizontalAngle is not None:
            if self._servos["horizontal"].current_angle == commandInstructions.horizontalAngle and self._servos["vertical"].current_angle == commandInstructions.verticalAngle:
                return "partially valid"
        elif commandInstructions.verticalAngle is not None:
            if self._servos["vertical"].current_angle == commandInstructions.verticalAngle:
                return "partially valid"
        elif commandInstructions.horizontalAngle is not None:
            if self._servos["horizontal"].current_angle == commandInstructions.horizontalAngle:
                return "partially valid"

        return "valid"

    def _center_servo_positions(self) -> None:
        for plane in list(self._servos.keys()):
            self._move_servo(plane, self._neutralAngle)

    def _move_servo(self, plane, angle) -> None:
        self._servos[plane].move_to_angle(angle)

    def _check_argument_validity(self, minAngles: dict[str: int], maxAngles: dict[str: int]) -> None:
        # check that angles are within the correct range
        RobocarHelper.check_if_num_is_in_interval(minAngles["horizontal"], -90, 1, "Minimum horizontal angle")
        RobocarHelper.check_if_num_is_in_interval(minAngles["vertical"], -90, 1, "Maximum vertical angle")

        RobocarHelper.check_if_num_is_in_interval(maxAngles["horizontal"], 1, 90, "Maximum horizontal angle")
        RobocarHelper.check_if_num_is_in_interval(maxAngles["vertical"], 1, 90, "Maximum vertical angle")


