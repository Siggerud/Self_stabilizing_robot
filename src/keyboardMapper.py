from data.commandContainers.honkCommands import HonkCommand
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from exceptions import InvalidCommandException
from utility.mapperHelper import check_for_duplicate_commands
from commandMapperBase import CommandMapperBase
from utility.yamlParser import get_float

class KeyboardMapper(CommandMapperBase):
    def __init__(self):
        self._VALID_KEYS = {
            *list("abcdefghijklmnopqrstuvwxyz"),
            *list("0123456789"),
            "`", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/",
            "space", "enter", "tab", "backspace",
            "up", "down", "left", "right",
            "esc", "ctrl", "ctrl+c", "shift", "alt",
        }

    def get_exit_command(self, globalSpecs: dict) -> str:
        return globalSpecs["keyboard"]["commands"]["exit"]

    def get_car_handling_commands(self, *args) -> dict:
        pass

    def get_honk_commands(self, honkSpecs: dict) -> dict:
        honkCommands = honkSpecs["keyboard"]["commands"]

        honkKey = honkCommands["honk"].lower()

        commands: dict[str: HonkCommand] = {
            self._create_press_key(honkKey): HonkCommand(startContinuousHonk=True),
            self._create_release_key(honkKey): HonkCommand(stopContinuousHonk=True)
        }

        return commands

    def get_camera_servo_handling_commands(self, cameraSpecs) -> dict:
        cameraHelperCommands = cameraSpecs["keyboard"]["commands"]

        displayKey: str = cameraHelperCommands["turn_display_on_or_off"].lower()
        zoomInKey: str = cameraHelperCommands["zoom_in"].lower()
        zoomOutKey: str = cameraHelperCommands["zoom_out"].lower()

        self._check_if_key_in_valid_keys([zoomInKey, zoomOutKey, displayKey])
        check_for_duplicate_commands([zoomInKey, zoomOutKey, displayKey], "CameraHandler")

        zoomIncrement = get_float(cameraSpecs["zoom"], "zoom_step")

        commands: dict[str: CameraHelperCommand] = {
            self._create_press_key(displayKey): CameraHelperCommand(changeDisplayActive=True),
            self._create_press_key(zoomInKey): CameraHelperCommand(zoomChange=zoomIncrement),
            self._create_press_key(zoomOutKey): CameraHelperCommand(zoomChange=-zoomIncrement)
        }

        return commands

    def get_command_descriptions(self, specs) -> dict:
        #TODO: move this to helper class
        commands: dict[str: str] = specs["keyboard"]["commands"]
        descriptions: dict[str: str] = specs["keyboard"]["command_descriptions"]

        # match the commands with their descriptions
        commandsToDescriptions: dict[str: str] = {commandValue: descValue for
                                                  (commandKey, commandValue, descKey, descValue) in
                                                  zip(commands.keys(), commands.values(), descriptions.keys(),
                                                      descriptions.values()) if commandKey == descKey}

        return commandsToDescriptions

    def get_camera_helper_commands(self, *args) -> dict:
        pass

    def _check_if_key_in_valid_keys(self, keys: list[str]):
        for key in keys:
            if key not in self._VALID_KEYS:
                raise InvalidCommandException(f"Key {key} not a valid key")

    def _create_press_key(self, key: str):
        return key + "_pressed"

    def _create_release_key(self, key: str):
        return key + "_released"
