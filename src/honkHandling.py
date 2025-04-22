from time import sleep
from utility.roboCarHelper import check_if_num_is_greater_than_or_equal_to_number
from commandExecutors import CommandExecutors
from hardware.buzzer import Buzzer
from src.data.commandContainers.honkCommand import HonkCommand

class HonkHandling(CommandExecutors):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, maxHonkTime: float, userCommands: dict, commandsToDescriptions: dict):
        self._check_argument_validity(defaultHonkTime, maxHonkTime)

        self._buzzer: Buzzer = Buzzer(buzzerPin)
        self._defaultHonkTime: float = defaultHonkTime
        self._maxHonkTime: float = maxHonkTime
        self._userCommands: dict[str: HonkCommand] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions

    @property
    def pins(self) -> list[int]:
        return [self._buzzer.pin]

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def __str__(self):
        return "Honk Handling"

    def setup(self) -> None:
        self._buzzer.setup()

    def cleanup(self) -> None:
        pass

    def get_command_validity(self, command: str) -> str:
        return "valid" # honking commands are always valid

    def handle_command(self, command: str) -> None:
        commandInstructions: HonkCommand = self._userCommands[command]
        if commandInstructions.singleHonk is not None:
            self._honk_for_set_time(self._defaultHonkTime)
        elif commandInstructions.honkForDuration is not None:
            self._honk_for_set_time(commandInstructions.honkForDuration)
        elif commandInstructions.startContinuousHonk is not None:
            self._start_honk()
        elif commandInstructions.stopContinuousHonk is not None:
            self._buzzer.stop_buzzing()

    def _start_honk(self) -> None:
        self._buzzer.start_buzzing()

    def _honk_for_set_time(self, honkTime: float) -> None:
        self._buzzer.start_buzzing()
        sleep(honkTime)
        self._buzzer.stop_buzzing()

    def _check_argument_validity(self, defaultHonkTime: float, maxHonkTime: float) -> None:
        check_if_num_is_greater_than_or_equal_to_number(defaultHonkTime, 0,"default honk time")
        check_if_num_is_greater_than_or_equal_to_number(maxHonkTime, 0,"max honk time")



