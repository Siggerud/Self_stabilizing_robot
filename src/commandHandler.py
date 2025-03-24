from multiprocessing import Pipe
from commandExecutors import CommandExecutors
from exceptions import InvalidCommandException
from robotProcess import RobotProcess

class CommandHandler(RobotProcess):
    def __init__(self, car, servo, cameraHelper, honk, signalLights, exitCommand):
        self._car = car
        self._servo = servo
        self._cameraHelper = cameraHelper
        self._honk = honk
        self._commandExecutors: list[CommandExecutors] = [
            self._car,
            self._servo,
            self._cameraHelper,
            self._honk
        ]

        self._check_command_validity()

        self._signalLights = signalLights
        self._exitCommand: str = exitCommand

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()

        self._commandValidityToSignalColor: dict = {
            "valid": "green",
            "partially valid": "yellow",
            "invalid": "red"
        }

        self._pipeReceiver, self._pipeSender = Pipe(duplex=False)

    @property
    def gpio_process(self) -> bool:
        return True

    @property
    def pipeSender(self) -> Pipe:
        return self._pipeSender

    @property
    def gpio_pins(self) -> list[int]:
        pins: list[int] = []
        for executor in self._commandExecutors:
            pins.extend(executor.pins)

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

            try:
                commandValidity: str = self._commandToObjects[command].get_command_validity(command)
            except KeyError:
                commandValidity: str = "invalid"

            # signal if the command was valid, partially valid or invalid
            signalColor = self._commandValidityToSignalColor[commandValidity]
            self._signalLights.blink(signalColor)

            # execute command if it is valid
            if commandValidity == "valid":
                self._commandToObjects[command].handle_command(command)
                self._cameraHelper.update_control_values_for_video_feed(shared_array)

    def setup(self):
        # setup objects
        for roboObject in self._commandExecutors:
            roboObject.setup()

        self._signalLights.setup()

        self._print_start_up_message()

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
                #TODO: print which objects have the duplicate command
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