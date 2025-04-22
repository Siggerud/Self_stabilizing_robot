from src.utility.roboCarHelper import check_if_num_is_in_interval
from commandExecutors import CommandExecutors
from commandContainers.cameraHelperCommand import CameraHelperCommand

class CameraHelper(CommandExecutors):
    def __init__(self, userCommands: dict[str: CameraHelperCommand], commandsToDescriptions: dict[str: str], maxZoomValue: float, zoomIncrement: float, car=None, servo=None):
        self._check_argument_validity(maxZoomValue, zoomIncrement)

        self._car = car
        self._servo = servo

        self._angleText: str = ""
        self._speedText: str = ""
        self._turnText: str = ""

        self._zoomValue: float = 1.0
        self._zoomIncrement: float = zoomIncrement

        self._minZoomValue: float = 1.0
        self._maxZoomValue: float = maxZoomValue

        self._userCommands: dict[str: CameraHelperCommand] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions

        self._hudActive: bool = True

        self._directionValue_to_number: dict = {
            "Stopped": 0,
            "Left": 1,
            "Right": 2,
            "Forward": 3,
            "Reverse": 4
        }

        self._arrayDict: dict[str: int] = None

    @property
    def pins(self) -> list[int]:
        return []

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    def __str__(self):
        return "Camera Helper"

    def setup(self) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def handle_command(self, command: CameraHelperCommand) -> None:
        commandInstructions = self._userCommands[command]
        if commandInstructions.displayActive is not None:
            self._set_hud_value(commandInstructions.displayActive)
        elif commandInstructions.changeDisplayActive is not None:
            self._set_hud_value(not self._hudActive)
        elif commandInstructions.zoomValue is not None:
            self._set_zoom_value(commandInstructions.zoomValue)
        elif commandInstructions.zoomChange is not None:
            self._increment_zoom_value(commandInstructions.zoomChange)

    def get_command_validity(self, command: str) -> str:
        commandInstructions = self._userCommands[command]
        if commandInstructions.displayActive is not None: # check if display is already on or off
            if self._hudActive == commandInstructions.displayActive:
                return "partially valid"

        elif commandInstructions.zoomValue is not None:
            if self._zoomValue == commandInstructions.zoomValue: # check if zoom value is unchanged
                return "partially valid"

        elif commandInstructions.zoomChange is not None:
            newZoomValue: float = self._zoomValue + commandInstructions.zoomChange
            if newZoomValue < self._minZoomValue:
                return "partially valid"
            elif newZoomValue > self._maxZoomValue:
                return "partially valid"

        return "valid"

    def add_car(self, car) -> None:
        self._car = car

    def add_servo(self, servo) -> None:
        self._servo = servo

    def update_control_values_for_video_feed(self, shared_array) -> None:
        if self._servo:
            shared_array[self._arrayDict["horizontal servo"]] = self._servo.get_current_servo_angle("horizontal")
            shared_array[self._arrayDict["vertical servo"]] = self._servo.get_current_servo_angle("vertical")

        if self._car:
            shared_array[self._arrayDict["speed"]] = self._car.current_speed
            shared_array[self._arrayDict["direction"]] = self._directionValue_to_number[self._car.current_turn_value]

        shared_array[self._arrayDict["HUD"]] = float(self._hudActive)
        shared_array[self._arrayDict["Zoom"]] = self._zoomValue

    def set_array_dict(self, arrayDict: dict[str: int]) -> None:
        self._arrayDict = arrayDict

    def _set_hud_value(self, command: bool) -> None:
        self._hudActive = command

    def _set_zoom_value(self, zoomValue: float) -> None:
        self._zoomValue = zoomValue

    def _increment_zoom_value(self, increment: float) -> None:
        newZoomValue = self._zoomValue + increment

        self._zoomValue = round(newZoomValue, 1) # round to nearest decimal to avoid rounding errors on camera feed

    def _check_argument_validity(self, maxZoomValue: float, zoomIncrement: float) -> None:
        check_if_num_is_in_interval(maxZoomValue, 1.0, 100.0, "MaximumZoomValue")
        check_if_num_is_in_interval(zoomIncrement, 0.1, 10.0, "ZoomIncrement")

