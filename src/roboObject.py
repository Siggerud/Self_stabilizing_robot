from exceptions import InvalidPinException, OutOfRangeException, InvalidCommandException
from raspberryPiPins import RaspberryPiPins

class RoboObject:
    _boardPinsInUse: list[int] = []
    _commandsInUse: list[str] = []

    def __init__(self, pins: list, commands: dict, **kwargs):
        piPins = RaspberryPiPins()
        self._boardPins = piPins.boardPins
        self._check_argument_validity(pins, commands, **kwargs)

    def cleanup(self) -> None:
        pass

    def setup(self) -> None:
        pass

    def get_command_validity(self, command: str) -> str:
        pass

    def print_commands(self) -> None:
        pass

    def handle_voice_command(self, command: str) -> None:
        pass

    def _check_argument_validity(self, pins: list[int], commands: dict[str, str], **kwargs) -> None:
        self._check_if_pins_are_valid(pins)
        self._check_command_length(commands)
        self._check_if_command_already_exists(commands)

    def _check_if_num_is_in_interval(self, num: int, lowerBound: int, upperBound: int, variableName: str) -> None:
        if num < lowerBound or num > upperBound:
            raise OutOfRangeException(f"{variableName} should be between {lowerBound} and {upperBound}")

    def _check_if_pins_are_valid(self, pins: list[int]) -> None:
        for pin in pins:
            # check that the pin number is a valid pin number
            if pin not in self._boardPins:
                raise InvalidPinException(f"Pin argument '{pin}' is not a valid pin number")

            # check that pin has not already been specified by another robo object class
            if pin in self._boardPinsInUse:
                raise InvalidPinException(f"Pin {pin} is already in use")

            self._add_pin_to_board_pins_in_use(pin)

    def _check_if_command_already_exists(self, commands: dict[str, str]) -> None:
        for command in list(commands.keys()):
            if command in self._commandsInUse:
                raise InvalidCommandException(f"Command {command} already exists")

            self._add_command_to_commands_in_use(command)

    def _check_if_num_is_greater_than_or_equal_to_number(self, num: int, lowerBound: int, variableName: str) -> None:
        if num <= lowerBound:
            raise OutOfRangeException(f"{variableName} should be greater than zero")

    def _check_command_length(self, commands: dict[str, str]) -> None:
        for command in list(commands.values()):
            if len(command.split()) < 2:
                raise InvalidCommandException(f"Command {command} is too short. Command should be minimum two words")

    def _check_for_placeholder_in_command(self, command: str) -> None:
        placeholder = "{param}"
        if placeholder not in command:
            raise InvalidCommandException(f"Command {command} is missing the {{param}} placeholder")

    def _print_commands(self, title: str, dicts: dict[str, str]) -> None:
        maxCommandLength = max(len(command) for command in dicts.keys()) + 1

        print(title)
        for command, v in dicts.items():
            print(f"{command.ljust(maxCommandLength)}: {v['description']}")
        print()

    def _format_command(self, command: str, param: str) -> str:
        return command.format(param=param)

    @classmethod
    def _add_pin_to_board_pins_in_use(cls, pin: int) -> None:
        cls._boardPinsInUse.append(pin)

    @classmethod
    def _add_command_to_commands_in_use(cls, command: str) -> None:
        cls._commandsInUse.append(command)




