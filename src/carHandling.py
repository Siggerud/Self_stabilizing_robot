from roboCarHelper import RobocarHelper
from roboObject import RoboObject
from motorDriver import MotorDriver


class CarHandling(RoboObject):
    def __init__(self,
                 motorDriver: MotorDriver,
                 pwmMinTT: int,
                 pwmMaxTT: int,
                 speedStep: int,
                 userCommands: dict):
        super().__init__(
            motorDriver.pins,
            {**userCommands["direction"], **userCommands["speed"]},
            pwmMinTT=pwmMinTT,
            pwmMaxTT=pwmMaxTT,
            speedStep=speedStep
        )
        self._motorDriver = motorDriver

        self._pwmMinTT: int = pwmMinTT
        self._pwmMaxTT: int = pwmMaxTT

        self._speedStep: int = speedStep

        self._speed: int = self._pwmMinTT

        self._direction: str = "Stopped"

        self._userCommands: dict = userCommands

        directionCommands: dict[str: str] = userCommands["direction"]
        self._direction_commands: dict[str: dict] = {
            directionCommands["turnLeftCommand"]: {"description": "Turns car left",
                                                   "direction": "Left"},
            directionCommands["turnRightCommand"]: {"description": "Turns car right",
                                                    "direction": "Right"},
            directionCommands["driveCommand"]: {"description": "Drives car forward",
                                                "direction": "Forward"},
            directionCommands["reverseCommand"]: {"description": "Reverses car",
                                                  "direction": "Reverse"},
            directionCommands["stopCommand"]: {"description": "Stops car",
                                               "direction": "Stopped"}
        }

        speedCommands: dict[str: str] = userCommands["speed"]
        self._speed_commands: dict[str: dict] = {
            speedCommands["increaseSpeedCommand"]: {"description": "Increases car speed",
                                                    "commandDescription": "increaseSpeedCommand"},
            speedCommands["decreaseSpeedCommand"]: {"description": "Decrease car speed",
                                                    "commandDescription": "decreaseSpeedCommand"}
        }

        self._exact_speed_commands: dict = self._set_exact_speed_commands(speedCommands["exactSpeedCommand"])

        # mainly for printing at startup
        self._variableCommands: dict[str: dict] = {
            speedCommands["exactSpeedCommand"].replace("param", "speed"): {
                "description": "Sets speed to the specified speed value"
            }
        }

    def setup(self) -> None:
        self._motorDriver.setup(self._speed)

    def handle_voice_command(self, command: str) -> None:
        if command in self._direction_commands:
            self._adjust_direction(self._direction_commands[command]["direction"])
        elif command in self._speed_commands or command in self._exact_speed_commands:
            self._adjust_speed(command)

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._direction_commands)
        allDictsWithCommands.update(self._speed_commands)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Car handling commands:"

        self._print_commands(title, allDictsWithCommands)

    def get_command_validity(self, command: str) -> str:
        # check if direction remains unchanged
        if command in self._direction_commands:
            if self._direction == self._direction_commands[command]["direction"]:
                return "partially valid"

        # check if speed remains unchanged
        elif command in self._exact_speed_commands:
            if self._speed == self._exact_speed_commands[command]:
                return "partially valid"

        # check if new speed increase/decrease is within valid range
        elif command in self._speed_commands:
            if command == self._userCommands["speed"]["increaseSpeedCommand"]:
                if (self._speed + self._speedStep) > self._pwmMaxTT:
                    return "partially valid"
            elif command == self._userCommands["speed"]["decreaseSpeedCommand"]:
                if (self._speed - self._speedStep) < self._pwmMinTT:
                    return "partially valid"

        return "valid"

    def cleanup(self) -> None:
        self._motorDriver.cleanup()

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._direction_commands,
                                                       self._speed_commands,
                                                       self._exact_speed_commands])

    @property
    def current_speed(self) -> int:
        return int(self._speed)

    @property
    def current_turn_value(self) -> str:
        return self._direction

    def _set_exact_speed_commands(self, userCommand: str) -> dict:
        speedCommands: dict = {}
        for speed in range(self._pwmMinTT, self._pwmMaxTT + 1):
            command = self._format_command(userCommand, str(speed))
            speedCommands[command] = speed

        return speedCommands

    def _adjust_direction_value(self, direction: str) -> None:
        self._direction = direction

    def _adjust_speed(self, command: str) -> None:
        adjustSpeed: bool = False

        if command == self._userCommands["speed"]["increaseSpeedCommand"]:
            self._speed += self._speedStep
            adjustSpeed = True
        elif command == self._userCommands["speed"]["decreaseSpeedCommand"]:
            self._speed -= self._speedStep
            adjustSpeed = True
        else:
            newSpeed = self._exact_speed_commands[command]
            if newSpeed != self._speed:
                adjustSpeed = True
                self._speed = newSpeed

        if adjustSpeed:
            self._change_speed()

    def _change_speed(self) -> None:
        #TODO: assert that speed is between 0 and 100

        self._motorDriver.change_speed(self._speed)

    def _adjust_direction(self, direction) -> None:
        if direction == "Forward":
            self._motorDriver.drive()
        elif direction == "Reverse":
            self._motorDriver.reverse()
        elif direction == "Left":
            self._motorDriver.turn_left()
        elif direction == "Right":
            self._motorDriver.turn_right()
        elif direction == "Stopped":
            self._motorDriver.stop()

        self._adjust_direction_value(direction)

    def _check_argument_validity(self, pins: list[int], userCommands: dict[str, str], **kwargs) -> None:
        super()._check_argument_validity(pins, userCommands, **kwargs)

        self._check_for_placeholder_in_command(userCommands["exactSpeedCommand"])

        # check that the pwm values are within valid range
        self._check_if_num_is_in_interval(kwargs["pwmMinTT"], 0, 100, "MinimumMotorPWM")
        self._check_if_num_is_in_interval(kwargs["pwmMaxTT"], 0, 100, "MaximumMotorPWM")

        # check that the speed step is within valid range
        self._check_if_num_is_in_interval(kwargs["speedStep"], 1, 100, "speed_step")
