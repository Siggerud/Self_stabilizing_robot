from multiprocessing import Queue
from roboObject import RoboObject

class CommandHandler:
    def __init__(self, car, servo, cameraHelper, honk, signalLights, exitCommand):
        self._car = car
        self._servo = servo
        self._cameraHelper = cameraHelper
        self._honk = honk
        self._roboObjects: list = [
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
                self._commandToObjects[command].handle_voice_command(command)
                self._cameraHelper.update_control_values_for_video_feed(shared_array)

    def _setup(self):
        # setup objects
        for roboObject in self._roboObjects:
            roboObject.setup()

        self._signalLights.setup()

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