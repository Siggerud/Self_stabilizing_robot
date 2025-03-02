from servo import Servo
from roboObject import RoboObject
from roboCarHelper import RobocarHelper
from servo import Servo

class CameraServoHandling(RoboObject):
    def __init__(self, horizontalServo: Servo, verticalServo: Servo, minAngles: list[int], maxAngles: list[int], userCommands: dict):
        super().__init__(
            [horizontalServo.servoPin, verticalServo.servoPin],
            {**userCommands["basicCommands"], **userCommands["exactAngleCommands"]},
            minAngles=minAngles,
            maxAngles=maxAngles
        )

        self._minAngles: dict = {
            "horizontal": minAngles[0],
            "vertical": minAngles[1]
        }

        self._maxAngles: dict = {
            "horizontal": maxAngles[0],
            "vertical": maxAngles[1]
        }

        self._servos: dict = {
            "horizontal": horizontalServo,
            "vertical": verticalServo
        }

        self._neutralAngle: int = 0

        basicCommands: dict = userCommands["basicCommands"]
        self._lookOffsetCommands: dict = {
            basicCommands["lookUpCommand"]: {
                "description": "Turns camera up",
                "plane": "vertical",
                "angle": self._maxAngles["vertical"]
            },
            basicCommands["lookDownCommand"]:
                {"description": "Turns camera down",
                 "plane": "vertical",
                 "angle": self._minAngles["vertical"]
                 },
            basicCommands["lookLeftCommand"]:
                {"description": "Turns camera left",
                 "plane": "horizontal",
                 "angle": self._maxAngles["horizontal"]
                 },
            basicCommands["lookRightCommand"]: {
                "description": "Turns camera right",
                "plane": "horizontal",
                "angle": self._minAngles["horizontal"]
            }
        }

        self._lookCenterCommand: dict = {
            basicCommands["lookCenterCommand"]: {
                "description": "Centers camera"
            }
        }

        variableAngleCommands: dict = userCommands["exactAngleCommands"]
        exactAngleCommands: dict = self._get_exact_angle_commands(variableAngleCommands)

        self._angleCommands: dict = {**self._lookOffsetCommands, **exactAngleCommands}

        # mainly for printing at startup
        self._variableCommands: dict = {
            variableAngleCommands["lookRightExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle to the right"
            },
            variableAngleCommands["lookLeftExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle to the left"
            },
            variableAngleCommands["lookUpExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle upwards"
            },
            variableAngleCommands["lookDownExact"].replace("param", "angle"): {
                "description": "Turns camera specified angle downwards"
            }
        }

    def setup(self) -> None:
        for servo in list(self._servos.values()):
            servo.setup()

        self._center_servo_positions()

    def handle_voice_command(self, command: str) -> None:
        if command in self._angleCommands:
            self._move_servo(self._angleCommands[command]["plane"],
                             self._angleCommands[command]["angle"]
                             )
        elif command in self._lookCenterCommand:
            self._center_servo_positions()

    def get_current_servo_angle(self, plane) -> int:
        return self._servos[plane].current_angle

    def cleanup(self) -> None:
        self._center_servo_positions()  # center camera when exiting
        for servo in list(self._servos.values()):
            servo.cleanup()

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._lookOffsetCommands)
        allDictsWithCommands.update(self._lookCenterCommand)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Servo handling commands:"

        self._print_commands(title, allDictsWithCommands)

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._angleCommands,self._lookCenterCommand])

    def get_command_validity(self, command: str) -> str:
        # check if angles stay unchanged
        if command in self._angleCommands:
            plane = self._angleCommands[command]["plane"]

            if self._servos[plane].current_angle == self._angleCommands[command]["angle"]:
                return "partially valid"

        elif command in self._lookCenterCommand:
            if self._servos["horizontal"].current_angle == self._neutralAngle and self._servos["vertical"].get_current_angle() == self._neutralAngle:
                return "partially valid"

        return "valid"

    def _center_servo_positions(self) -> None:
        for plane in list(self._servos.keys()):
            self._move_servo(plane, self._neutralAngle)

    def _move_servo(self, plane, angle) -> None:
        self._servos[plane].move_to_angle(angle)

    def _get_exact_angle_commands(self, userCommands: dict) -> dict:
        exactAngleCommands: dict = {}

        # looking right commands
        plane: str = "horizontal"
        angleRange: range = range(self._minAngles[plane], 0)
        command: str = userCommands["lookRightExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking left commands
        plane: str = "horizontal"
        angleRange: range = range(1, self._maxAngles[plane] + 1)
        command: str = userCommands["lookLeftExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking down commands
        plane: str = "vertical"
        angleRange: range = range(self._minAngles[plane], 0)
        command: str = userCommands["lookDownExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking up commands
        plane: str = "vertical"
        angleRange: range = range(1, self._maxAngles[plane] + 1)
        command: str = userCommands["lookUpExact"]
        exactAngleCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        return exactAngleCommands

    def _get_angle_commands_for_given_direction(self, range, command, plane) -> dict:
        exactAngleCommands: dict = {}

        for angle in range:
            userCommand: str = self._format_command(command, str(abs(angle))) # take the absolute value, because the user will always say a positive value
            exactAngleCommands[userCommand] = {
                "plane": plane,
                "angle": angle
            }

        return exactAngleCommands

    def _check_argument_validity(self, pins: list, userCommands: dict, **kwargs) -> None:
        super()._check_argument_validity(pins, userCommands, **kwargs)

        self._check_for_placeholder_in_command(userCommands["lookRightExact"])
        self._check_for_placeholder_in_command(userCommands["lookLeftExact"])
        self._check_for_placeholder_in_command(userCommands["lookUpExact"])
        self._check_for_placeholder_in_command(userCommands["lookDownExact"])

        # check that angles are within the correct range
        self._check_if_num_is_in_interval(kwargs["minAngles"][0], -90, 1, "Minimum horizontal angle")
        self._check_if_num_is_in_interval(kwargs["minAngles"][1], -90, 1, "Maximum vertical angle")

        self._check_if_num_is_in_interval(kwargs["maxAngles"][0], 1, 90, "Maximum horizontal angle")
        self._check_if_num_is_in_interval(kwargs["maxAngles"][1], 1, 90, "Maximum vertical angle")


