import logging
from multiprocessing import Pipe

from commandExecutors import CommandExecutors
from data.instructionContainers.stabilizerInstruction import StabilizerInstruction


class StabilizerHelper(CommandExecutors):
    def __init__(self, userCommands: dict[str: StabilizerInstruction], commandsToDescriptions: dict[str: str],
                 pipe: Pipe, loggerProcessName: str):
        self._logger = logging.getLogger(loggerProcessName)

        self._userCommands = userCommands
        self._commandsToDescriptions = commandsToDescriptions
        self._pipe = pipe

    def handle_command(self, command: str) -> None:
        self._pipe.send(command)  # Send the command through the pipe

    @property
    def pins(self) -> list[int]:
        return []  # TODO: implement this

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def cleanup(self) -> None:
        self._logger.info("Stabilizer helper cleaned up.")

    def setup(self) -> None:
        self._logger.info("Setting up stabilizer helper...")

    def get_command_validity(self, command: str) -> str:
        return "valid"  # TODO: implement this

    def __str__(self):
        return "Stabilizer Helper"
