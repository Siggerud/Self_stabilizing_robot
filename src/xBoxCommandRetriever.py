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
        minStick = -1
        maxStick = 1
        stepValue = 0.02
        commands = {}
        for stickValue in [round(float(x), 2) for x in np.arange(minStick, maxStick + stepValue, stepValue)]:
            stickValueToAngle = map_value_to_new_scale(stickValue, minAngles["vertical"], maxAngles["vertical"], minStick, maxStick)
            commands[f"LSB vertical {stickValue}"] = CameraServoCommand(verticalAngle=int(stickValueToAngle))

        print(commands)
        return {}

    def get_car_handling_commands(self, *args) -> dict:
        return {}

    def get_command_descriptions(self, *args) -> dict:
        return {}

    def get_camera_helper_commands(self, *args) -> dict:
        return {}