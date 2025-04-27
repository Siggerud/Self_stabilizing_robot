from commandMapperBase import CommandMapperBase
from data.commandContainers.honkCommand import HonkCommand
from data.commandContainers.cameraServoCommand import CameraServoCommand
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from data.commandContainers.carHandlingCommands import CarHandlingCommand
import numpy as np
from utility.roboCarHelper import map_value_to_new_scale

#TODO: get everything from config files
class XBoxCommandMapper(CommandMapperBase):
    def get_exit_command(self, globalSpecs: dict) -> str:
        return globalSpecs["xbox"]["commands"]["exit"] + " press"

    def get_honk_commands(self, honkSpecs: dict) -> dict:
        honkCommands = honkSpecs["xbox"]["commands"]

        honkButton = honkCommands["honk"]

        commands: dict[str: HonkCommand] = {
            f"{honkButton} press": HonkCommand(startContinuousHonk=True),
            f"{honkButton} release": HonkCommand(stopContinuousHonk=True)
        }

        return commands

    def get_camera_servo_handling_commands(self, servoSpecs: dict) -> dict:
        # RSB stick
        servoCommands: dict = servoSpecs["xbox"]["commands"]

        servoSticks: dict[str: str] = {
            "horizontal": servoCommands["move_horizontal"],
            "vertical": servoCommands["move_vertical"]
        }

        minAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["min_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["min_angle"]
        }

        maxAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["max_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["max_angle"]
        }

        commands: dict[str: CameraServoCommand] = {}
        commands.update(self._get_angle_commands_for_given_plane("horizontal", servoSticks, minAngles, maxAngles))
        commands.update(self._get_angle_commands_for_given_plane("vertical", servoSticks, minAngles, maxAngles))

        return commands

    def _get_angle_commands_for_given_plane(self, plane, servoSticks, minAngles, maxAngles):
        minStick: int = -1
        maxStick: int = 1
        stickValue: float = minStick
        stepValue: float = 0.01
        commands: dict[str: CameraServoCommand] = {}
        while stickValue <= maxStick:
            stickValueToAngle = int(map_value_to_new_scale(stickValue, minAngles[plane], maxAngles[plane],
                                                     maxStick, minStick))
            #TODO: the stepvalue needs to be the same as in xBoxEventHandler, maybe every 0.01?
            if plane == "horizontal":
                instruction = CameraServoCommand(horizontalAngle=stickValueToAngle)
            elif plane == "vertical":
                instruction = CameraServoCommand(verticalAngle=stickValueToAngle)
            commands[f"{servoSticks[plane]} {plane} {round(stickValue, 2)}"] = instruction

            stickValue += stepValue

        return commands

    def get_car_handling_commands(self, carHandlingSpecs: dict) -> dict:
        carHandlingCommands: dict[str: str] = carHandlingSpecs["xbox"]["commands"]

        driveTrigger: str = carHandlingCommands["drive"]
        reverseTrigger: str = carHandlingCommands["reverse"]
        turnStick: str = carHandlingCommands["turning"]

        commands: dict[str: CarHandlingCommand] = {}


        # generate commands for drive and reverse
        minStickValue: float = -1
        stickValue = minStickValue
        maxStickValue: float = 1
        stepValue = 0.01
        while stickValue <= maxStickValue:
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, -1, 1))
            commands[f"{driveTrigger} {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Forward")
            commands[f"{reverseTrigger} {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Reverse")

            stickValue += stepValue

        # generate commands for turning left
        stickValue = minStickValue
        while stickValue < 0: # from -1 to -0.01
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, 0, -1))
            commands[f"{turnStick} horizontal {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Left")

            stickValue += stepValue

        # generate command for when turning stick i centered
        commands[f"{turnStick} horizontal {0.0}"] = CarHandlingCommand(speedValue=0, movement="Stopped")

        # generate commands for turning right
        stickValue = 0 + stepValue
        while stickValue <= 1: # from 0.01 to 1
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, 0, 1))
            commands[f"{turnStick} horizontal {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Right")

            stickValue += stepValue

        return commands

    def get_command_descriptions(self, specs: dict) -> dict[str: str]:
        commands: dict[str: str] = specs["xbox"]["commands"]
        descriptions: dict[str: str] = specs["xbox"]["command_descriptions"]

        # match the commands with their descriptions
        commandsToDescriptions: dict[str: str] = {commandValue: descValue for
                                                  (commandKey, commandValue, descKey, descValue) in
                                                  zip(commands.keys(), commands.values(), descriptions.keys(),
                                                      descriptions.values()) if commandKey == descKey}

        return commandsToDescriptions

    def get_camera_helper_commands(self, cameraSpecs: dict) -> dict:
        cameraHelperCommands = cameraSpecs["xbox"]["commands"]

        displayButton: str = cameraHelperCommands["turn_display_on_or_off"]
        zoomInButton: str = cameraHelperCommands["zoom_in"]
        zoomOutButton: str = cameraHelperCommands["zoom_out"]

        zoomIncrement = float(cameraSpecs["zoom"]["zoom_step"])

        commands: dict[str: CameraHelperCommand] = {
            f"{displayButton} press": CameraHelperCommand(changeDisplayActive=True),
            f"{zoomInButton} press": CameraHelperCommand(zoomChange=zoomIncrement),
            f"{zoomOutButton} press": CameraHelperCommand(zoomChange=-zoomIncrement)
        }

        return commands