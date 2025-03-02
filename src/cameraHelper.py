from roboCarHelper import RobocarHelper
from roboObject import RoboObject

class CameraHelper(RoboObject):
    def __init__(self, userCommands: dict, maxZoomValue: float, zoomIncrement: float, car=None, servo=None):
        super().__init__(
            [],
            {**userCommands["hudCommands"], **userCommands["zoomCommands"]},
            maxZoomValue=maxZoomValue,
            zoomIncrement=zoomIncrement
        )

        self._car = car
        self._servo = servo

        self._angleText: str = ""
        self._speedText: str = ""
        self._turnText: str = ""

        self._zoomValue: float = 1.0
        self._zoomIncrement: float = zoomIncrement

        self._minZoomValue: float = 1.0
        self._maxZoomValue: float = maxZoomValue

        self._hudActive: bool = True

        self._directionValue_to_number: dict = {
            "Stopped": 0,
            "Left": 1,
            "Right": 2,
            "Forward": 3,
            "Reverse": 4
        }

        self._userCommands: dict = userCommands

        hudCommands: dict = userCommands["hudCommands"]
        self._hudCommands: dict = {
            hudCommands["turnOnDisplayCommand"]: {"description": "Turns on HUD", "hudValue": True},
            hudCommands["turnOffDisplayCommand"]: {"description": "Turns off HUD", "hudValue": False}
        }

        zoomCommands: dict = userCommands["zoomCommands"]
        self._zoomExactCommands: dict = self._set_zoom_commands(zoomCommands["zoomExactCommand"])

        self._zoomIncrementCommands: dict = {
            zoomCommands["zoomInCommand"]: {"description": "zooms in by the default increment value"},
            zoomCommands["zoomOutCommand"]: {"description": "zooms out by the default increment value"}
        }

        self._arrayDict: dict[str: int] = None

        # mainly for printing at startup
        self._variableCommands: dict[str: dict] = {
            zoomCommands["zoomExactCommand"].replace("param", "zoom"): {
                "description": "Zooms camera to the specified zoom value"
            }
        }

    def handle_voice_command(self, command: str) -> None:
        print(command)
        if command in self._hudCommands:
            self._set_hud_value(command)
        elif command in self._zoomExactCommands:
            self._set_zoom_value(command)
        elif command in self._zoomIncrementCommands:
            self._increment_zoom_value(command)

    def print_commands(self) -> None:
        allDictsWithCommands: dict = {}
        allDictsWithCommands.update(self._hudCommands)
        allDictsWithCommands.update(self._zoomIncrementCommands)
        allDictsWithCommands.update(self._variableCommands)
        title: str = "Camera commands:"

        self._print_commands(title, allDictsWithCommands)

    def get_command_validity(self, command: str) -> str:
        if command in self._hudCommands: # check if display is already on or off
            if self._hudActive == self._hudCommands[command]["hudValue"]:
                return "partially valid"

        elif command in self._zoomExactCommands:
            if self._zoomValue == self._zoomExactCommands[command]: # check if zoom value is unchanged
                return "partially valid"

        elif command in self._zoomIncrementCommands:
            if command == self._userCommands["zoomCommands"]["zoomOutCommand"]:
                if (self._zoomValue - self._zoomIncrement) < self._minZoomValue:
                    return "partially valid"
            elif command == self._userCommands["zoomCommands"]["zoomInCommand"]:
                if (self._zoomValue + self._zoomIncrement) > self._maxZoomValue:
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

    def get_voice_commands(self) -> list:
        return RobocarHelper.chain_together_dict_keys([
            self._hudCommands,
            self._zoomExactCommands,
            self._zoomIncrementCommands
        ])

    def set_array_dict(self, arrayDict: dict[str: int]) -> None:
        self._arrayDict = arrayDict

    def _set_hud_value(self, command: str) -> None:
        self._hudActive = self._hudCommands[command]["hudValue"]

    def _set_zoom_value(self, command: str) -> None:
        self._zoomValue = self._zoomExactCommands[command]

    def _increment_zoom_value(self, command: str) -> None:
        if command == self._userCommands["zoomCommands"]["zoomOutCommand"]:
            self._zoomValue -= self._zoomIncrement
        elif command == self._userCommands["zoomCommands"]["zoomInCommand"]:
            self._zoomValue += self._zoomIncrement

        self._zoomValue = round(self._zoomValue, 1) # round to nearest decimal to avoid rounding errors on camera feed

    def _set_zoom_commands(self, userCommand: str) -> dict:
        zoomValue: float = self._minZoomValue
        stepValue: float = 0.1
        zoomCommands: dict = {}
        while zoomValue <= (self._maxZoomValue + stepValue):
            command: str = self._format_command(userCommand, str(round(zoomValue, 1)))
            zoomCommands[command] = round(zoomValue, 1) # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue

        return zoomCommands

    def _check_argument_validity(self, pins: list, userCommands: dict, **kwargs) -> None:
        super()._check_argument_validity(pins, userCommands, **kwargs)

        self._check_for_placeholder_in_command(userCommands["zoomExactCommand"])

        self._check_if_num_is_in_interval(kwargs["maxZoomValue"], 1.0, 100.0, "MaximumZoomValue")

        self._check_if_num_is_in_interval(kwargs["zoomIncrement"], 0.1, 10.0, "ZoomIncrement")

