import logging

from utility.roboCarHelper import check_if_num_is_in_interval
from commandExecutors import CommandExecutors
from data.instructionContainers.cameraHelperInstruction import CameraHelperInstruction

class CameraHandler(CommandExecutors):
    def __init__(self, userCommands: dict[str: CameraHelperInstruction], commandsToDescriptions: dict[str: str], maxZoomValue: float, zoomIncrement: float, loggerProcessName: str):
        self._logger = logging.getLogger(loggerProcessName)

        self._check_argument_validity(maxZoomValue, zoomIncrement)

        self._zoomValue: float = 1.0
        self._zoomIncrement: float = zoomIncrement

        self._minZoomValue: float = 1.0
        self._maxZoomValue: float = maxZoomValue

        self._userCommands: dict[str: CameraHelperInstruction] = userCommands
        self._commandsToDescriptions: dict[str: str] = commandsToDescriptions

        self._hudActive: bool = True

    @property
    def pins(self) -> list[int]:
        return []

    @property
    def commands(self) -> list[str]:
        return list(self._userCommands.keys())

    @property
    def command_descriptions(self) -> dict[str: str]:
        return self._commandsToDescriptions

    @property
    def hudValue(self) -> bool:
        return self._hudActive

    @property
    def zoomValue(self) -> float:
        return self._zoomValue

    def __str__(self):
        return "Camera Helper"

    def setup(self) -> None:
        self._logger.info("Setting up camera handler...")

    def cleanup(self) -> None:
        pass

    def handle_command(self, command: CameraHelperInstruction) -> None:
        instructions = self._userCommands[command]
        if instructions.displayActive is not None:
            self._set_hud_value(instructions.displayActive)
        elif instructions.changeDisplayActive is not None:
            self._set_hud_value(not self._hudActive)
        elif instructions.zoomValue is not None:
            self._set_zoom_value(instructions.zoomValue)
        elif instructions.zoomChange is not None:
            self._increment_zoom_value(instructions.zoomChange)

    def get_command_validity(self, command: str) -> str:
        instructions = self._userCommands[command]
        if instructions.displayActive is not None: # check if display is already on or off
            if self._hudActive == instructions.displayActive:
                return "partially valid"

        elif instructions.zoomValue is not None:
            if self._zoomValue == instructions.zoomValue: # check if zoom value is unchanged
                return "partially valid"

        elif instructions.zoomChange is not None:
            newZoomValue: float = self._zoomValue + instructions.zoomChange
            if newZoomValue < self._minZoomValue:
                return "partially valid"
            elif newZoomValue > self._maxZoomValue:
                return "partially valid"

        return "valid"

    def _set_hud_value(self, state: bool) -> None:
        self._hudActive = state

    def _set_zoom_value(self, zoomValue: float) -> None:
        self._zoomValue = zoomValue

    def _increment_zoom_value(self, increment: float) -> None:
        newZoomValue = self._zoomValue + increment

        self._zoomValue = round(newZoomValue, 1) # round to nearest decimal to avoid rounding errors on camera feed

    def _check_argument_validity(self, maxZoomValue: float, zoomIncrement: float) -> None:
        check_if_num_is_in_interval(maxZoomValue, 1.0, 100.0, "MaximumZoomValue")
        check_if_num_is_in_interval(zoomIncrement, 0.1, 10.0, "ZoomIncrement")

