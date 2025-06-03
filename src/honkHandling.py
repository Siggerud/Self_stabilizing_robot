import logging
from time import sleep
from utility.roboCarHelper import check_if_num_is_greater_than_or_equal_to_number
from commandExecutors import CommandExecutors
from hardware.buzzer import Buzzer
from data.instructionContainers.honkInstruction import HonkInstruction

class HonkHandling(CommandExecutors):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, userCommands: dict, commandsToDescriptions: dict, processName: str):
        self._logger = logging.getLogger(processName)

        self._check_argument_validity(defaultHonkTime)

        self._buzzer: Buzzer = Buzzer(buzzerPin)
        self._defaultHonkTime: float = defaultHonkTime
        self._commandsToInstructions: dict[str: HonkInstruction] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions

    @property
    def pins(self) -> list[int]:
        return [self._buzzer.pin]

    @property
    def commands(self) -> list[str]:
        return list(self._commandsToInstructions.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def __str__(self):
        return "Honk Handling"

    def setup(self) -> None:
        self._logger.info("Setting up honk handler...")

        self._buzzer.setup()

    def cleanup(self) -> None:
        pass

    def get_command_validity(self, command: str) -> str:
        return "valid" # honking commands are always valid

    def handle_command(self, command: str) -> None:
        instructions: HonkInstruction = self._commandsToInstructions[command]
        if instructions.singleHonk is not None:
            self._honk_for_set_time(self._defaultHonkTime)
        elif instructions.honkForDuration is not None:
            self._honk_for_set_time(instructions.honkForDuration)
        elif instructions.startContinuousHonk is not None:
            self._start_honk()
        elif instructions.stopContinuousHonk is not None:
            self._buzzer.stop_buzzing()

    def _start_honk(self) -> None:
        self._buzzer.start_buzzing()

    def _honk_for_set_time(self, honkTime: float) -> None:
        self._buzzer.start_buzzing()
        sleep(honkTime)
        self._buzzer.stop_buzzing()

    def _check_argument_validity(self, defaultHonkTime: float) -> None:
        check_if_num_is_greater_than_or_equal_to_number(defaultHonkTime, 0,"default honk time")



