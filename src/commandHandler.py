from multiprocessing import Pipe
from typing import Optional
from urllib.robotparser import RobotFileParser

from cameraHelper import CameraHelper
from commandExecutors import CommandExecutors
from exceptions import InvalidCommandException
from robotTask import RobotTask
from signalLights import SignalLights


class CommandHandler(RobotTask):
    def __init__(self, commandExecutors: list[CommandExecutors], cameraHelper: Optional[CameraHelper],
                 signalLights: Optional[SignalLights], exitCommand: str):
        self._commandExecutors = commandExecutors
        self._cameraHelper = cameraHelper

        self._check_command_validity()

        self._signalLights = signalLights
        self._exitCommand = exitCommand

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()

        self._commandValidityToSignalColor: dict = {
            "valid": "green",
            "partially valid": "yellow",
            "invalid": "red"
        }

        self._pipeReceiver: Optional[Pipe] = None

    @property
    def gpio_process(self) -> bool:
        return True

    @property
    def gpio_pins(self) -> list[int]:
        pins: list[int] = []
        for executor in self._commandExecutors:
            pins.extend(executor.pins)

        if self._signalLights is not None:
            pins.extend(self._signalLights.pins)

        return pins

    def cleanup(self) -> None:
        # cleanup objects
        for roboObject in self._commandExecutors:
            roboObject.cleanup()

    def execute_commands(self, flag, shared_array) -> None:
        while not flag.value:
            command: str = self._pipeReceiver.recv()

            if command == self._exitCommand:
                break

            commandValidity: str = self._get_validity_of_command(command)

            if self._signalLights is not None:
                self._give_led_signal_on_command_validity(commandValidity)

            # execute command if it is valid
            if commandValidity == "valid":
                self._process_command(command, shared_array)

    def setup(self, pipeReceiver: Pipe) -> None:
        self._pipeReceiver = pipeReceiver

        # setup objects
        for roboObject in self._commandExecutors:
            roboObject.setup()

        if self._signalLights is not None:
            self._signalLights.setup()

        self._print_start_up_message()

    def _process_command(self, command: str, shared_array) -> None:
        self._commandToObjects[command].handle_command(command)
        self._update_camera_feed_values(shared_array)

    def _update_camera_feed_values(self, shared_array) -> None:
        if self._cameraHelper is not None:
            self._cameraHelper.update_control_values_for_video_feed(shared_array)

    def _give_led_signal_on_command_validity(self, commandValidity: str) -> None:
        # signal if the command was valid, partially valid or invalid
        signalColor = self._commandValidityToSignalColor[commandValidity]
        self._signalLights.blink(signalColor)

    def _get_validity_of_command(self, command: str) -> str:
        try:
            return self._commandToObjects[command].get_command_validity(command)
        except KeyError:
            return "invalid"

    def _check_command_validity(self) -> None:
        # validate commands
        commands: list[str] = []
        for executor in self._commandExecutors:
            commands.extend(executor.commands)

        # check for duplicate commands across all objects
        self._check_if_command_already_exists(commands)

    def _print_start_up_message(self) -> None:
        for executor in self._commandExecutors:
            self._print_commands(str(executor), executor.command_descriptions)

        print(f"Exit command : {self._exitCommand}")
        print()

    def _check_if_command_already_exists(self, commands: dict[str: str]) -> None:
        commandsInUse: list[str] = []
        for command in commands:
            if command in commandsInUse:
                # TODO: print which objects have the duplicate command
                raise InvalidCommandException(f"Command {command} already exists")

            commandsInUse.append(command)

    def _get_all_objects_mapped_to_commands(self) -> dict[str: CommandExecutors]:
        objectsToCommands: dict[str: CommandExecutors] = {}

        # add commands from all robot objects
        for executor in self._commandExecutors:
            objectsToCommands.update(self._add_object_to_commands(executor))

        return objectsToCommands

    def _add_object_to_commands(self, executor) -> dict[str: CommandExecutors]:
        objectToCommands: dict[str: CommandExecutors] = {}
        for command in executor.commands:
            objectToCommands[command] = executor

        return objectToCommands

    def _print_commands(self, title: str, commandsToDescriptions: dict[str, str]) -> None:
        maxCommandLength = max(len(command) for command in commandsToDescriptions.keys()) + 1

        print(title)
        for command, description in commandsToDescriptions.items():
            print(f"{command.ljust(maxCommandLength)}: {description}")
        print()
