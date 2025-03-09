from multiprocessing import Queue
from roboObject import RoboObject
from exceptions import InvalidPinException, InvalidCommandException
from raspberryPiPins import RaspberryPiPins
from roboCarHelper import RobocarHelper

class CommandHandler:
    def __init__(self, car, servo, cameraHelper, honk, signalLights, exitCommand):
        self._car = car
        self._servo = servo
        self._cameraHelper = cameraHelper
        self._honk = honk
        self._roboObjects: list[RoboObject] = [
            self._car,
            self._servo,
            self._cameraHelper,
            self._honk
        ]
        self._signalLights = signalLights
        self._exitCommand: str = exitCommand

        self._commandToObjects: dict[str: object] = self._get_all_objects_mapped_to_commands()

        self._commandValidityToSignalColor: dict = {
            "valid": "green",
            "partially valid": "yellow",
            "invalid": "red"
        }

        self._queue = Queue()

    @property
    def queue(self) -> Queue:
        return self._queue

    def print_start_up_message(self) -> None:
        for roboObject in self._roboObjects:
            roboObject.print_commands()

        print(f"Exit command : {self._exitCommand}")
        print()

    def cleanup(self) -> None:
        # cleanup objects
        for roboObject in self._roboObjects:
            roboObject.cleanup()

    def execute_commands(self, flag, shared_array) -> None:
        self._setup()

        while not flag.value:
            command: str = self._queue.get()

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
        #TODO: consider moving validation to init
        self._check_command_validity()
        self._check_pins_validity()

        # setup objects
        for roboObject in self._roboObjects:
            roboObject.setup()

        self._signalLights.setup()

    def _check_pins_validity(self) -> None:
        # validate pins
        pins: list[int] = []
        for roboObject in self._roboObjects:
            pins.extend(roboObject.pins)

        try:
            self._check_if_pin_is_a_valid_pin_number(pins)
            self._check_if_pins_already_in_use(pins)
        except InvalidPinException as e:
            RobocarHelper.print_startup_error(e)

    def _check_command_validity(self) -> None:
        # validate commands
        commands: list[str] = []
        for roboObject in self._roboObjects:
            commands.extend(roboObject.commands)

        try:
            self._check_if_command_already_exists(commands)
            self._check_command_length(commands)
            self._check_for_placeholders_in_commands(commands)
        except InvalidCommandException as e:
            RobocarHelper.print_startup_error(e)

    def _check_for_placeholders_in_commands(self, commands: dict[str: str]) -> None:
        placeholder = "{param}"
        paramKey = "_param"
        for command in commands.keys():
            if paramKey in command: # check for any keys with the paramKey in it
                if placeholder not in command: # any keys with paramkeys need to contain the placeholder
                    raise InvalidCommandException(f"Command {command} is missing the {{param}} placeholder")

    def _check_command_length(self, commands: dict[str: str]) -> None:
        for command in commands.keys():
            if len(command.split()) < 2:
                raise InvalidCommandException(f"Command {command} is too short. Command should be minimum two words")

    def _check_if_command_already_exists(self, commands: dict[str: str]) -> None:
        commandsInUse: list[str] = []
        for command in commands.keys():
            if command in commandsInUse:
                raise InvalidCommandException(f"Command {command} already exists")

            commandsInUse.append(command)

    def _check_if_pin_is_a_valid_pin_number(self, pins: list[int]) -> None:
        boardPins: tuple[int] = RaspberryPiPins().boardPins
        for pin in pins:
            # check that the pin number is a valid pin number
            if pin not in boardPins:
                raise InvalidPinException(f"Pin argument '{pin}' is not a valid pin number")

    def _check_if_pins_already_in_use(self, pins: list[int]) -> None:
        boardPinsInUse: list[int] = []
        for pin in pins:
            # check that pin has not already been specified by another robo object class
            if pin in boardPinsInUse:
                raise InvalidPinException(f"Pin {pin} is already in use")

            boardPinsInUse.append(pin)

    def _get_all_objects_mapped_to_commands(self) -> dict[str: RoboObject]:
        objectsToCommands: dict[str: RoboObject] = {}

        # add commands from all robot objects
        for roboObject in self._roboObjects:
            objectsToCommands.update(self._add_object_to_commands(roboObject))

        return objectsToCommands

    def _add_object_to_commands(self, roboObject) -> dict[str: RoboObject]:
        objectToCommands: dict[str: RoboObject] = {}
        for command in roboObject.get_voice_commands():
            objectToCommands[command] = roboObject

        return objectToCommands