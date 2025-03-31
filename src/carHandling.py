from roboCarHelper import check_if_num_is_in_interval
from commandExecutors import CommandExecutors
from motorDriver import MotorDriver
from commandContainers.carHandlingCommands import CarHandlingCommand

class CarHandling(CommandExecutors):
    def __init__(self,
                 motorDriver: MotorDriver,
                 pwmMin: int,
                 pwmMax: int,
                 speedStep: int,
                 userCommands: dict,
                 commandsToDescriptions: dict):
        self._check_argument_validity(pwmMin, pwmMax, speedStep)

        self._motorDriver = motorDriver

        self._pwmMin: int = pwmMin
        self._pwmMax: int = pwmMax

        self._speedStep: int = speedStep
        self._speed: int = self._pwmMin

        self._direction: str = "Stopped"

        self._userCommands: dict[str: CarHandlingCommand] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions

    @property
    def pins(self) -> list[int]:
        return self._motorDriver.pins

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def __str__(self) -> str:
        return "Car Handling"

    def setup(self) -> None:
        self._motorDriver.setup(self._speed)

    def handle_command(self, command: str) -> None:
        commandInstructions: CarHandlingCommand = self._userCommands[command]
        if commandInstructions.movement is not None:
            self._adjust_direction(commandInstructions.movement)
        elif commandInstructions.speedValue is not None:
            self._change_speed(commandInstructions.speedValue)
        elif commandInstructions.speedChange is not None:
            self._increment_speed(commandInstructions.speedChange)

    def get_command_validity(self, command: str) -> str:
        commandInstructions: CarHandlingCommand = self._userCommands[command]

        # check if direction remains unchanged
        if commandInstructions.movement is not None:
            if self._direction == commandInstructions.movement:
                return "partially valid"

        # check if speed remains unchanged
        elif commandInstructions.speedValue is not None:
            if self._speed == commandInstructions.speedValue:
                return "partially valid"

        # check if new speed increase/decrease is within valid range
        elif commandInstructions.speedChange is not None:
            newSpeedValue: int = self._speed + commandInstructions.speedChange
            #TODO: after changing speed range from pwm values to 0 to 100, change this check accordingly
            if newSpeedValue > self._pwmMax:
                return "partially valid"
            if newSpeedValue < self._pwmMin:
                return "partially valid"

        return "valid"

    def cleanup(self) -> None:
        self._motorDriver.cleanup()

    @property
    def current_speed(self) -> int:
        return int(self._speed)

    @property
    def current_turn_value(self) -> str:
        return self._direction

    def _adjust_direction_value(self, direction: str) -> None:
        self._direction = direction

    def _increment_speed(self, speedChange: int) -> None:
        newSpeed = self._speed + speedChange
        self._change_speed(newSpeed)

    def _change_speed(self, speed) -> None:
        assert 100 >= speed >= 0

        self._speed = speed
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

    def _check_argument_validity(self, pwmMin: int, pwmMax: int, speedStep: int) -> None:
        # check that the pwm values are within valid range
        check_if_num_is_in_interval(pwmMin, 0, 100, "MinimumMotorPWM")
        check_if_num_is_in_interval(pwmMax, 0, 100, "MaximumMotorPWM")

        # check that the speed step is within valid range
        check_if_num_is_in_interval(speedStep, 1, 100, "speed_step")
