from commandRetriever import CommandRetriever
from commandContainers.honkCommand import HonkCommand
from commandContainers.cameraServoCommand import CameraServoCommand
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
        stepValue: float = 0.05
        commands: dict[str: CameraServoCommand] = {}
        for stickValue in [round(float(x), 2) for x in np.arange(minStick, maxStick + stepValue, stepValue)]:
            stickValueToAngle = int(map_value_to_new_scale(stickValue, minAngles[plane], maxAngles[plane],
                                                       minStick, maxStick))
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

    def get_camera_helper_commands(self, *args) -> dict:
        return {}