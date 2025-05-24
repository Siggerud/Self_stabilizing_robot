from data.commandContainers.honkCommands import HonkCommand
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from data.commandContainers.carHandlingCommands import CarHandlingCommand
from data.commandContainers.cameraServoCommand import CameraServoCommand
from exceptions import InvalidCommandException
from utility.mapperHelper import check_for_duplicate_commands
from commandMapperBase import CommandMapperBase
from utility.yamlParser import get_float, get_int

class KeyboardMapper(CommandMapperBase):
    def __init__(self):
        self._VALID_KEYS = {
            *list("abcdefghijklmnopqrstuvwxyz"),
            *list("0123456789"),
            "`", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/",
            "space", "enter", "tab", "backspace",
            "up", "down", "left", "right", "end",
            "esc"
        }

    def get_exit_command(self, globalSpecs: dict) -> str:
        return globalSpecs["keyboard"]["commands"]["exit"]

    def get_car_handling_commands(self, carHandlingSpecs) -> dict:
        carHandlingCommands: dict[str: str] = carHandlingSpecs["keyboard"]["commands"]

        driveKey: str = carHandlingCommands["drive"].lower()
        reverseKey: str = carHandlingCommands["reverse"].lower()
        turnLeftKey: str = carHandlingCommands["turn_left"].lower()
        turnRightKey: str = carHandlingCommands["turn_right"].lower()

        defaultSpeed: int = get_int(carHandlingSpecs["keyboard"], "default_speed")

        self._check_if_keys_in_valid_keys([driveKey, reverseKey, turnLeftKey, turnRightKey])
        check_for_duplicate_commands([driveKey, reverseKey, turnLeftKey, turnRightKey], "CarHandling")

        # generate command for when turning stick i centered
        commands: dict[str: CarHandlingCommand] = {
            self._create_press_key(driveKey): CarHandlingCommand(speedValue=defaultSpeed, movement="Forward"),
            self._create_release_key(driveKey): CarHandlingCommand(speedValue=0, movement="Stopped"),
            self._create_press_key(reverseKey): CarHandlingCommand(speedValue=defaultSpeed, movement="Reverse"),
            self._create_release_key(reverseKey): CarHandlingCommand(speedValue=0, movement="Stopped"),
            self._create_press_key(turnLeftKey): CarHandlingCommand(speedValue=defaultSpeed, movement="Left"),
            self._create_release_key(turnLeftKey): CarHandlingCommand(speedValue=0, movement="Stopped"),
            self._create_press_key(turnRightKey): CarHandlingCommand(speedValue=defaultSpeed, movement="Right"),
            self._create_release_key(turnRightKey): CarHandlingCommand(speedValue=0, movement="Stopped"),
        }

        return commands

    def get_honk_commands(self, honkSpecs: dict) -> dict:
        honkCommands = honkSpecs["keyboard"]["commands"]

        honkKey = honkCommands["honk"].lower()

        commands: dict[str: HonkCommand] = {
            self._create_press_key(honkKey): HonkCommand(startContinuousHonk=True),
            self._create_release_key(honkKey): HonkCommand(stopContinuousHonk=True)
        }

        return commands

    def get_camera_servo_handling_commands(self, servoSpecs) -> dict:
        servoCommands: dict = servoSpecs["keyboard"]["commands"]

        lookUpCommand = servoCommands["look_up"]
        lookDownCommand = servoCommands["look_down"]
        lookLeftCommand = servoCommands["look_left"]
        lookRightCommand = servoCommands["look_right"]
        lookCenterCommand = servoCommands["look_center"]

        self._check_if_keys_in_valid_keys([lookUpCommand, lookDownCommand, lookLeftCommand, lookRightCommand, lookCenterCommand])
        check_for_duplicate_commands([lookUpCommand, lookDownCommand, lookLeftCommand, lookRightCommand, lookCenterCommand], "CameraServoHandling")

        minAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["min_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["min_angle"]
        }

        maxAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["max_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["max_angle"]
        }

        commands: dict[str: CameraServoCommand] = {
            self._create_press_key(lookUpCommand): CameraServoCommand(verticalAngle=maxAngles["vertical"], horizontalAngle=0),
            self._create_press_key(lookDownCommand): CameraServoCommand(verticalAngle=minAngles["vertical"], horizontalAngle=0),
            self._create_press_key(lookLeftCommand): CameraServoCommand(horizontalAngle=maxAngles["horizontal"], verticalAngle=0),
            self._create_press_key(lookRightCommand): CameraServoCommand(horizontalAngle=minAngles["horizontal"], verticalAngle=0),
            self._create_press_key(lookCenterCommand): CameraServoCommand(horizontalAngle=0, verticalAngle=0)
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

    def get_camera_helper_commands(self, cameraSpecs) -> dict:
        cameraHelperCommands = cameraSpecs["keyboard"]["commands"]

        displayKey: str = cameraHelperCommands["turn_display_on_or_off"].lower()
        zoomInKey: str = cameraHelperCommands["zoom_in"].lower()
        zoomOutKey: str = cameraHelperCommands["zoom_out"].lower()

        self._check_if_keys_in_valid_keys([zoomInKey, zoomOutKey, displayKey])
        check_for_duplicate_commands([zoomInKey, zoomOutKey, displayKey], "CameraHandler")

        zoomIncrement = get_float(cameraSpecs["zoom"], "zoom_step")

        commands: dict[str: CameraHelperCommand] = {
            self._create_press_key(displayKey): CameraHelperCommand(changeDisplayActive=True),
            self._create_press_key(zoomInKey): CameraHelperCommand(zoomChange=zoomIncrement),
            self._create_press_key(zoomOutKey): CameraHelperCommand(zoomChange=-zoomIncrement)
        }

        return commands

    def _check_if_keys_in_valid_keys(self, keys: list[str]):
        for key in keys:
            if key not in self._VALID_KEYS:
                raise InvalidCommandException(f"Key {key} not a valid key")

    def _create_press_key(self, key: str) -> str:
        return key + "_pressed"

    def _create_release_key(self, key: str) -> str:
        return key + "_released"
