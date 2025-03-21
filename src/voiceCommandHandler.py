from configparser import SectionProxy
from roboCarHelper import RobocarHelper
from commandContainers.cameraHelperCommand import CameraHelperCommand
from commandContainers.cameraServoCommand import CameraServoCommand
from commandContainers.honkCommand import HonkCommand
from commandContainers.carHandlingCommands import CarHandlingCommand

class VoiceCommandHandler:
    def __init__(self):
        pass

    def get_car_handling_commands(self, carHandlingCommands: SectionProxy, speedStep: int, pwmMin: int, pwmMax: int) -> dict:
        turnLeftCommand = carHandlingCommands["turn_left"]
        turnRightCommand = carHandlingCommands["turn_right"]
        driveCommand = carHandlingCommands["drive"]
        reverseCommand = carHandlingCommands["reverse"]
        stopCommand = carHandlingCommands["stop"]

        increaseSpeedCommand = carHandlingCommands["increase_speed"]
        decreaseSpeedCommand = carHandlingCommands["decrease_speed"]
        exactSpeedCommand_param = carHandlingCommands["exact_speed"]

        newCommands: dict[str: CarHandlingCommand] = {
            turnLeftCommand: CarHandlingCommand(movement="Left"),
            turnRightCommand: CarHandlingCommand(movement="Right"),
            driveCommand: CarHandlingCommand(movement="Forward"),
            reverseCommand: CarHandlingCommand(movement="Reverse"),
            stopCommand: CarHandlingCommand(movement="Stopped"),
            increaseSpeedCommand: CarHandlingCommand(speedChange=speedStep),
            decreaseSpeedCommand: CarHandlingCommand(speedChange=-speedStep)
        }

        for speed in range(pwmMin, pwmMax + 1):
            command = RobocarHelper.format_command(exactSpeedCommand_param, str(speed))
            newCommands.update({command: CarHandlingCommand(speedValue=speed)})

        return newCommands

    def get_honk_commands(self, honkCommands: SectionProxy, maxHonkTime: float) -> dict:
        honkCommand = honkCommands["honk"]
        honkForSpecifiedTimeCommand_param = honkCommands["honk_for_specified_time"]

        newCommands: dict[str: HonkCommand] = {
            honkCommand: HonkCommand(singleHonk=True),
        }

        honkTime: float = 0.1
        stepValue: float = 0.1
        while honkTime <= (maxHonkTime + stepValue):
            command: str = RobocarHelper.format_command(honkForSpecifiedTimeCommand_param, str(round(honkTime, 1)))
            newCommands.update({command: HonkCommand(honkForDuration=round(honkTime, 1))})  # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return newCommands

    def get_camera_servo_handling_commands(self, servoCommands: SectionProxy, minAngles: dict[str: int], maxAngles: dict[str: int]) -> dict:
        lookUpCommand = servoCommands["look_up"]
        lookDownCommand = servoCommands["look_down"]
        lookLeftCommand = servoCommands["look_left"]
        lookRightCommand = servoCommands["look_right"]
        lookCenterCommand = servoCommands["look_center"]

        lookUpExact = servoCommands["look_up_exact"]
        lookDownExact = servoCommands["look_down_exact"]
        lookLeftExact = servoCommands["look_left_exact"]
        lookRightExact = servoCommands["look_right_exact"]

        newCommands: dict[str: CameraServoCommand] = {
            lookUpCommand: CameraServoCommand(verticalAngle=maxAngles["vertical"], horizontalAngle=0),
            lookDownCommand: CameraServoCommand(verticalAngle=minAngles["vertical"], horizontalAngle=0),
            lookLeftCommand: CameraServoCommand(horizontalAngle=maxAngles["horizontal"], verticalAngle=0),
            lookRightCommand: CameraServoCommand(horizontalAngle=minAngles["horizontal"], verticalAngle=0),
            lookCenterCommand: CameraServoCommand(horizontalAngle=0, verticalAngle=0)
        }

        # looking right commands
        plane: str = "horizontal"
        angleRange: range = range(minAngles[plane], 0)
        command: str = lookRightExact
        newCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking left commands
        plane: str = "horizontal"
        angleRange: range = range(1, maxAngles[plane] + 1)
        command: str = lookLeftExact
        newCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking down commands
        plane: str = "vertical"
        angleRange: range = range(minAngles[plane], 0)
        command: str = lookDownExact
        newCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        # looking up commands
        plane: str = "vertical"
        angleRange: range = range(1, maxAngles[plane] + 1)
        command: str = lookUpExact
        newCommands.update(
            self._get_angle_commands_for_given_direction(angleRange, command, plane)
        )

        return newCommands

    def _get_angle_commands_for_given_direction(self, range, command, plane) -> dict:
        exactAngleCommands: dict = {}

        for angle in range:
            userCommand: str = RobocarHelper.format_command(command, str(abs(angle))) # take the absolute value, because the user will always say a positive value
            if plane == "vertical":
                exactAngleCommands[userCommand] = CameraServoCommand(
                    verticalAngle=angle
                )
            elif plane == "horizontal":
                exactAngleCommands[userCommand] = CameraServoCommand(
                    horizontalAngle=angle
                )

        return exactAngleCommands

    def get_camera_helper_commands(self, commands: SectionProxy, minZoomValue: float, maxZoomValue: float, stepValue: float) -> dict:
        turnOnDisplayCommand = commands["turn_on_display"]
        turnOffDisplayCommand = commands["turn_off_display"]

        zoomExactCommand_param = commands["zoom"]
        zoomInCommand = commands["zoom_in"]
        zoomOutCommand = commands["zoom_out"]

        newCommands: dict[str: CameraHelperCommand] = {
            turnOnDisplayCommand: CameraHelperCommand(displayActive=True),
            turnOffDisplayCommand: CameraHelperCommand(displayActive=False),
            zoomInCommand: CameraHelperCommand(zoomChange=stepValue),
            zoomOutCommand: CameraHelperCommand(zoomChange=-stepValue)
        }

        zoomValue: float = minZoomValue
        stepValue: float = 0.1
        while zoomValue <= (maxZoomValue + stepValue):
            command: str = RobocarHelper.format_command(zoomExactCommand_param, str(round(zoomValue, 1)))
            newCommands.update({command: CameraHelperCommand(zoomValue=round(zoomValue, 1))})  # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue

        return newCommands

