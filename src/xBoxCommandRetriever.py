from commandRetriever import CommandRetriever
from commandContainers.honkCommand import HonkCommand
from commandContainers.cameraServoCommand import CameraServoCommand
from commandContainers.cameraHelperCommand import CameraHelperCommand
import numpy as np
from roboCarHelper import map_value_to_new_scale

#TODO: get everything from config files
class XBoxCommandRetriever(CommandRetriever):
    def get_honk_commands(self, *args) -> dict:
        return {"X press": HonkCommand(startContinuousHonk=True),
                "X release": HonkCommand(stopContinuousHonk=True)}

    def get_camera_servo_handling_commands(self, servoCommands: dict[str: str], minAngles: dict[str: int],
                                           maxAngles: dict[str: int]) -> dict:
        # LSB stick
        commands: dict = {}
        commands.update(self._get_angle_commands_for_given_plane("horizontal", minAngles, maxAngles))
        commands.update(self._get_angle_commands_for_given_plane("vertical", minAngles, maxAngles))

        return commands

    def _get_angle_commands_for_given_plane(self, plane, minAngles, maxAngles):
        minStick: int = -1
        maxStick: int = 1
        stepValue: float = 0.1
        commands: dict[str: CameraServoCommand] = {}
        for stickValue in [round(float(x), 2) for x in np.arange(minStick, maxStick + stepValue, stepValue)]:
            stickValueToAngle = int(map_value_to_new_scale(stickValue, minAngles[plane], maxAngles[plane],
                                                       maxStick, minStick))
            if plane == "horizontal":
                instruction = CameraServoCommand(horizontalAngle=stickValueToAngle)
            elif plane == "vertical":
                instruction = CameraServoCommand(verticalAngle=stickValueToAngle)
            commands[f"LSB {plane} {stickValue}"] = instruction

        return commands

    def get_car_handling_commands(self, *args) -> dict:
        return {}

    def get_command_descriptions(self, *args) -> dict:
        return {}

    def get_camera_helper_commands(self, commands: dict[str: str], minZoomValue: float, maxZoomValue: float,
                                   stepValue: float) -> dict:
        commands = {
            "Y press": CameraHelperCommand(changeDisplayActive=True)
        }

        for stickValue in [round(float(x), 2) for x in np.arange(-1, 0 + stepValue, stepValue)]:
            stickValueToZoomValue = int(map_value_to_new_scale(stickValue, 1, maxZoomValue, 0, -1))
            commands[f"RSB vertical {stickValue}"] = CameraHelperCommand(zoomValue=stickValueToZoomValue)

        return commands