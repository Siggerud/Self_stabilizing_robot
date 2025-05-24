from data.instructionContainers.cameraServoInstruction import CameraServoInstruction
from commandExecutors import CommandExecutors
from utility.roboCarHelper import check_if_num_is_in_interval
from hardware.servo import Servo

class CameraServoHandling(CommandExecutors):
    def __init__(self,
                 horizontalServo: Servo,
                 verticalServo: Servo,
                 minAngles: dict,
                 maxAngles: dict,
                 userCommands: dict,
                 commandsToDescriptions: dict):
        self._check_argument_validity(minAngles, maxAngles)

        self._commandsToInstructions: dict[str: CameraServoInstruction] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions
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
        return list(self._commandsToInstructions.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def __str__(self) -> str:
        return "Camera Servo Handling"

    def setup(self) -> None:
        for servo in list(self._servos.values()):
            servo.setup()

        self._center_servo_positions()

    def handle_command(self, command: str) -> None:
        instructions: CameraServoInstruction = self._commandsToInstructions[command]
        if instructions.verticalAngle is not None and instructions.horizontalAngle is not None:
            self._move_servo("vertical", instructions.verticalAngle)
            self._move_servo("horizontal", instructions.horizontalAngle)
        elif instructions.horizontalAngle is not None:
            self._move_servo("horizontal", instructions.horizontalAngle)
        elif instructions.verticalAngle is not None:
            self._move_servo("vertical", instructions.verticalAngle)

    def get_current_servo_angle(self, plane) -> int:
        return self._servos[plane].current_angle

    def cleanup(self) -> None:
        self._center_servo_positions()  # center camera when exiting
        for servo in list(self._servos.values()):
            servo.cleanup()

    def get_command_validity(self, command: str) -> str:
        # check if angles stay unchanged
        instructions: CameraServoInstruction = self._commandsToInstructions[command]
        if instructions.verticalAngle is not None and instructions.horizontalAngle is not None:
            if self._servos["horizontal"].current_angle == instructions.horizontalAngle and self._servos["vertical"].current_angle == instructions.verticalAngle:
                return "partially valid"
        elif instructions.verticalAngle is not None:
            if self._servos["vertical"].current_angle == instructions.verticalAngle:
                return "partially valid"
        elif instructions.horizontalAngle is not None:
            if self._servos["horizontal"].current_angle == instructions.horizontalAngle:
                return "partially valid"

        return "valid"

    def _center_servo_positions(self) -> None:
        for plane in list(self._servos.keys()):
            self._move_servo(plane, self._neutralAngle)

    def _move_servo(self, plane, angle) -> None:
        self._servos[plane].move_to_angle(angle)

    def _check_argument_validity(self, minAngles: dict[str: int], maxAngles: dict[str: int]) -> None:
        # check that angles are within the correct range
        check_if_num_is_in_interval(minAngles["horizontal"], -90, 1, "Minimum horizontal angle")
        check_if_num_is_in_interval(minAngles["vertical"], -90, 1, "Maximum vertical angle")

        check_if_num_is_in_interval(maxAngles["horizontal"], 1, 90, "Maximum horizontal angle")
        check_if_num_is_in_interval(maxAngles["vertical"], 1, 90, "Maximum vertical angle")


