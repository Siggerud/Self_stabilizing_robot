from roboCarHelper import check_if_num_is_in_interval
from commandExecutors import CommandExecutors
from motorDriver import MotorDriver
from commandContainers.carHandlingCommands import CarHandlingCommand

class CarHandling(CommandExecutors):
    def __init__(self,
                 motorDriver: MotorDriver,
                 speedStep: int,
                 userCommands: dict,
                 commandsToDescriptions: dict):
        self._check_argument_validity(speedStep)

        self._motorDriver = motorDriver

        self._minimumSpeed: int = 0
        self._maximumSpeed: int = 100

        self._speedStep: int = speedStep
        self._speed: int = 0

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
        if commandInstructions.speedValue is not None:
            self._change_speed(commandInstructions.speedValue)
        if commandInstructions.speedChange is not None:
            self._increment_speed(commandInstructions.speedChange)

    def get_command_validity(self, command: str) -> str:
        commandInstructions: CarHandlingCommand = self._userCommands[command]

        # check if direction remains unchanged
        if commandInstructions.movement is not None and commandInstructions.speedValue is not None:
            if self._direction == commandInstructions.movement and self._speed == commandInstructions.speedValue:
                return "partially valid"

        elif commandInstructions.movement is not None:
            if self._direction == commandInstructions.movement:
                return "partially valid"

        # check if speed remains unchanged
        elif commandInstructions.speedValue is not None:
            if self._speed == commandInstructions.speedValue:
                return "partially valid"

        # check if new speed increase/decrease is within valid range
        elif commandInstructions.speedChange is not None:
            newSpeedValue: int = self._speed + commandInstructions.speedChange

            if newSpeedValue > self._maximumSpeed:
                return "partially valid"
            if newSpeedValue < self._minimumSpeed:
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

        if self._speed == speed:
            return

        self._speed = speed
        self._motorDriver.change_speed(self._speed)

    def _adjust_direction(self, direction) -> None:
        if self._direction == direction:
            return

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

    def _check_argument_validity(self, speedStep: int) -> None:
        # check that the speed step is within valid range
        check_if_num_is_in_interval(speedStep, 1, 100, "speed_step")
