from time import sleep
from roboCarHelper import RobocarHelper
from commandExecutors import CommandExecutors
from buzzer import Buzzer
from commandContainers.honkCommand import HonkCommand

class HonkHandling(CommandExecutors):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, maxHonkTime: float, userCommands: dict):
        self._check_argument_validity(defaultHonkTime, maxHonkTime)

        self._buzzer: Buzzer = Buzzer(buzzerPin)
        self._defaultHonkTime: float = defaultHonkTime
        self._maxHonkTime: float = maxHonkTime
        self._userCommands: dict[str: HonkCommand] = userCommands

    @property
    def pins(self) -> list[int]:
        return [self._buzzer.pin]

    @property
    def commands(self) -> dict[str: str]:
        #TODO: implement
        return {}

    def setup(self) -> None:
        self._buzzer.setup()

    def cleanup(self) -> None:
        pass

    def get_command_validity(self, command: str) -> str:
        return "valid" # honking commands are always valid

    def handle_command(self, command: str) -> None:
        commandInstuctions: HonkCommand = self._userCommands[command]
        if commandInstuctions.singleHonk is not None:
            self._honk(self._defaultHonkTime)
        elif commandInstuctions.honkForDuration is not None:
            self._honk(commandInstuctions.honkForDuration)

    def print_commands(self) -> None:
        # allDictsWithCommands: dict = {**self._honkCommand, **self._variableCommands}
        # title: str = "Honk commands:"
        #
        # RobocarHelper.print_commands(title, allDictsWithCommands)
        pass

    def get_voice_commands(self) -> list[str]:
        return list(self._userCommands.keys())

    def _honk(self, honkTime: float) -> None:
        self._buzzer.start_buzzing()
        sleep(honkTime)
        self._buzzer.stop_buzzing()

    def _check_argument_validity(self, defaultHonkTime: float, maxHonkTime: float) -> None:
        RobocarHelper.check_if_num_is_greater_than_or_equal_to_number(defaultHonkTime, 0,"default honk time")
        RobocarHelper.check_if_num_is_greater_than_or_equal_to_number(maxHonkTime, 0,"max honk time")



