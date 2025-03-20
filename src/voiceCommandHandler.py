from configparser import SectionProxy
from roboCarHelper import RobocarHelper
from commandContainers.cameraHelperCommand import CameraHelperCommand

class VoiceCommandHandler:
    def __init__(self):
        pass

    def get_camera_helper_commands(self, commands: SectionProxy, minZoomValue: float, maxZoomValue: float, stepValue: float) -> dict:
        turnOnDisplayCommand = commands["turn_on_display"]
        turnOffDisplayCommand = commands["turn_off_display"]

        zoomExactCommand_param = commands["zoom"]
        zoomInCommand = commands["zoom_in"]
        zoomOutCommand = commands["zoom_out"]

        newCommands: dict[str: CameraHelperCommand] = {
            turnOnDisplayCommand: CameraHelperCommand(True, None, None),
            turnOffDisplayCommand: CameraHelperCommand(False, None, None),
            zoomInCommand: CameraHelperCommand(None, None, stepValue),
            zoomOutCommand: CameraHelperCommand(None, None, -stepValue)
        }

        zoomValue: float = minZoomValue
        stepValue: float = 0.1
        while zoomValue <= (maxZoomValue + stepValue):
            command: str = RobocarHelper.format_command(zoomExactCommand_param, str(round(zoomValue, 1)))
            newCommands.update({command: CameraHelperCommand(None, round(zoomValue, 1), None)})  # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue
        print(newCommands)
        return newCommands

