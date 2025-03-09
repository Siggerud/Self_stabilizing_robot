from time import sleep
from roboCarHelper import RobocarHelper
from roboObject import RoboObject
from buzzer import Buzzer

class HonkHandling(RoboObject):
    def __init__(self, buzzerPin: int, defaultHonkTime: float, maxHonkTime: float, userCommands: dict):
        self._check_argument_validity(defaultHonkTime, maxHonkTime)

        self._buzzer: Buzzer = Buzzer(buzzerPin)
        self._defaultHonkTime: float = defaultHonkTime
        self._maxHonkTime: float = maxHonkTime
        self._userCommands: dict[str: str] = userCommands

        self._honkCommand: dict[str: dict] = {userCommands["honkCommand"]: {"description": "Starts honking"}}
        self._honkForSpecifiedTimeCommands: dict[str: float] = self._set_honk_for_specified_time_commands(userCommands["honkForSpecifiedTimeCommand"])

        # mainly for printing at startup
        self._variableCommands: dict[str: dict] = {
            userCommands["honkForSpecifiedTimeCommand"].replace("param", "time"): {
                "description": "Honks for the specified time"
            }
        }

    @property
    def pins(self) -> list[int]:
        return [self._buzzer.pin]

    @property
    def commands(self) -> dict[str: str]:
        return self._userCommands.values()

    def setup(self) -> None:
        self._buzzer.setup()

    def cleanup(self) -> None:
        pass

    def get_command_validity(self, command: str) -> str:
        return "valid" # honking commands are always valid

    def handle_command(self, command: str) -> None:
        if command in self._honkCommand:
            honkTime: float = self._defaultHonkTime
        elif command in self._honkForSpecifiedTimeCommands:
            honkTime: float = self._honkForSpecifiedTimeCommands[command]
        self._honk(honkTime)

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {**self._honkCommand, **self._variableCommands}
        title: str = "Honk commands:"

        RobocarHelper.print_commands(title, allDictsWithCommands)

    def get_voice_commands(self) -> list[str]:
        return RobocarHelper.chain_together_dict_keys([self._honkCommand,
                                                       self._honkForSpecifiedTimeCommands]
                                                      )

    def _honk(self, honkTime: float) -> None:
        self._buzzer.start_buzzing()
        sleep(honkTime)
        self._buzzer.stop_buzzing()

    def _set_honk_for_specified_time_commands(self, userCommand: str) -> dict[str, float]:
        honkTime: float = 0.1
        stepValue: float = 0.1
        honkCommands: dict = {}
        while honkTime <= (self._maxHonkTime + stepValue):
            command: str = RobocarHelper.format_command(userCommand, str(round(honkTime, 1)))
            honkCommands[command] = round(honkTime, 1) # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return honkCommands

    def _check_argument_validity(self, defaultHonkTime: float, maxHonkTime: float) -> None:
        RobocarHelper.check_if_num_is_greater_than_or_equal_to_number(defaultHonkTime, 0,"default honk time")

        RobocarHelper.check_if_num_is_greater_than_or_equal_to_number(maxHonkTime, 0,"max honk time")



