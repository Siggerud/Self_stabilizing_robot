from data.commandContainers.honkCommands import HonkCommand
from exceptions import InvalidCommandException
from utility.mapperHelper import check_for_duplicate_commands

class KeyboardMapper:
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

        honkButton = honkCommands["honk"].lower()

        commands: dict[str: HonkCommand] = {
            honkButton + "_pressed": HonkCommand(startContinuousHonk=True),
            honkButton + "_released": HonkCommand(stopContinuousHonk=True)
        }

        return commands

    def get_camera_servo_handling_commands(self, *args) -> dict:
        pass

    def get_command_descriptions(self, *args) -> dict:
        pass

    def get_camera_helper_commands(self, *args) -> dict:
        pass

    def _check_if_key_in_valid_keys(self, keys: list[str]):
        for key in keys:
            if key not in self._VALID_KEYS:
                raise InvalidCommandException(f"Key {key} not a valid key")
