from multiprocessing import Pipe
from commandExecutors import CommandExecutors
from raspberryPiPins import RaspberryPiPins
from exceptions import InvalidPinException, InvalidCommandException
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

        self._validateRoboObjects()

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

    def print_start_up_message(self) -> None:
        for roboObject in self._commandExecutors:
            roboObject.print_commands()

        print(f"Exit command : {self._exitCommand}")
        print()

    def cleanup(self) -> None:
        # cleanup objects
        for roboObject in self._commandExecutors:
            roboObject.cleanup()

    def execute_commands(self, flag, shared_array) -> None:
        self._setup()

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

    def _setup(self):
        # setup objects
        for roboObject in self._commandExecutors:
            roboObject.setup()

        self._signalLights.setup()

    def _check_command_validity(self) -> None:
        # validate commands
        commands: dict[str: str] = {}
        for executor in self._commandExecutors:
            commands.update(executor.commands)

        self._check_if_command_already_exists(commands)
        self._check_command_length(commands)
        self._check_for_placeholders_in_commands(commands)


    def _check_for_placeholders_in_commands(self, commands: dict[str: str]) -> None:
        placeholder = "{param}"
        paramKey = "_param"
        for commandKey, commandValue in commands.items():
            if paramKey in commandKey: # check for any keys with the paramKey in it
                if placeholder not in commandValue: # any keys with paramkeys need to contain the placeholder
                    raise InvalidCommandException(f"Command {commandKey} is missing the {{param}} placeholder")

    def _check_command_length(self, commands: dict[str: str]) -> None:
        for command in commands.values():
            print(command)
            if len(command.split()) < 2:
                raise InvalidCommandException(f"Command {command} is too short. Command should be minimum two words")

    def _check_if_command_already_exists(self, commands: dict[str: str]) -> None:
        commandsInUse: list[str] = []
        for command in commands.keys():
            if command in commandsInUse:
                raise InvalidCommandException(f"Command {command} already exists")

            commandsInUse.append(command)

    def _get_all_objects_mapped_to_commands(self) -> dict[str: CommandExecutors]:
        objectsToCommands: dict[str: CommandExecutors] = {}

        # add commands from all robot objects
        for roboObject in self._commandExecutors:
            objectsToCommands.update(self._add_object_to_commands(roboObject))

        return objectsToCommands

    def _add_object_to_commands(self, roboObject) -> dict[str: CommandExecutors]:
        objectToCommands: dict[str: CommandExecutors] = {}
        for command in roboObject.get_voice_commands():
            objectToCommands[command] = roboObject

        return objectToCommands