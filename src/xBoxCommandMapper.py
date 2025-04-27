from commandMapperBase import CommandMapperBase
from data.commandContainers.honkCommand import HonkCommand
from data.commandContainers.cameraServoCommand import CameraServoCommand
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from data.commandContainers.carHandlingCommands import CarHandlingCommand
import numpy as np
from utility.roboCarHelper import map_value_to_new_scale

#TODO: get everything from config files
class XBoxCommandMapper(CommandMapperBase):
    def get_honk_commands(self, honkSpecs: dict) -> dict:
        honkCommands = honkSpecs["xbox"]["commands"]

        honkButton = honkCommands["honk"]

        commands: dict[str: HonkCommand] = {
            f"{honkButton} press": HonkCommand(startContinuousHonk=True),
            f"{honkButton} release": HonkCommand(stopContinuousHonk=True)
        }

        return commands

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
        stepValue: float = 0.1 #TODO: step value is used wrongly here
        commands: dict[str: CameraServoCommand] = {}
        for stickValue in [round(float(x), 2) for x in np.arange(minStick, maxStick + stepValue, stepValue)]:
            stickValueToAngle = int(map_value_to_new_scale(stickValue, minAngles[plane], maxAngles[plane],
                                                     maxStick, minStick))
            #TODO: the stepvalue needs to be the same as in xBoxEventHandler, maybe every 0.01?
            if plane == "horizontal":
                instruction = CameraServoCommand(horizontalAngle=stickValueToAngle)
            elif plane == "vertical":
                instruction = CameraServoCommand(verticalAngle=stickValueToAngle)
            commands[f"LSB {plane} {stickValue}"] = instruction

        return commands

    def get_car_handling_commands(self, *args) -> dict:
        commands = {
            "D-PAD left press": CarHandlingCommand(movement="Left", speedValue=100),
            "D-PAD left release": CarHandlingCommand(movement="Stopped", speedValue=100),
            "D-PAD right press": CarHandlingCommand(movement="Right", speedValue=100),
            "D-PAD right release": CarHandlingCommand(movement="Stopped", speedValue=100)
        }

        stickValue = -1
        stepValue = 0.1
        while stickValue <= 1:
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, -1, 1))
            commands[f"RT {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Forward")
            commands[f"LT {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Reverse")

            stickValue += stepValue

        return commands


    def get_command_descriptions(self, *args) -> dict:
        return {}

    def get_camera_helper_commands(self, commands: dict[str: str], minZoomValue: float, maxZoomValue: float,
                                   stepValue: float) -> dict:
        commands = {
            "Y press": CameraHelperCommand(changeDisplayActive=True)
        }
        # TODO: step value is used wrongly here
        for stickValue in [round(float(x), 2) for x in np.arange(-1, 0 + stepValue, stepValue)]:
            stickValueToZoomValue = int(map_value_to_new_scale(stickValue, 1, maxZoomValue, 0, -1))
            commands[f"RSB vertical {stickValue}"] = CameraHelperCommand(zoomValue=stickValueToZoomValue)

        return commands