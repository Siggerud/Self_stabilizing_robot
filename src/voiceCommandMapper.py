from commandContainers.cameraHelperCommand import CameraHelperCommand
from commandContainers.cameraServoCommand import CameraServoCommand
from commandContainers.carHandlingCommands import CarHandlingCommand
from commandContainers.honkCommand import HonkCommand
from exceptions import InvalidCommandException
from src.utility.roboCarHelper import format_command
from commandMapperBase import CommandMapperBase

class VoiceCommandMapper(CommandMapperBase):
    def __init__(self):
        pass

    def get_car_handling_commands(self, carHandlingCommands: dict[str: str], speedStep: int) -> dict:
        self._check_for_placeholders_in_commands("exact_speed", carHandlingCommands["exact_speed"])

        turnLeftCommand = carHandlingCommands["turn_left"]
        turnRightCommand = carHandlingCommands["turn_right"]
        driveCommand = carHandlingCommands["drive"]
        reverseCommand = carHandlingCommands["reverse"]
        stopCommand = carHandlingCommands["stop"]

        increaseSpeedCommand = carHandlingCommands["increase_speed"]
        decreaseSpeedCommand = carHandlingCommands["decrease_speed"]
        exactSpeedCommand_param = carHandlingCommands["exact_speed"]

        allCommands = [
            turnLeftCommand,
            turnRightCommand,
            driveCommand,
            reverseCommand,
            stopCommand,
            increaseSpeedCommand,
            decreaseSpeedCommand,
            exactSpeedCommand_param
        ]

        self._check_for_duplicate_commands(allCommands, "CarHandling")
        self._check_command_length(allCommands, "CarHandling")

        newCommands: dict[str: CarHandlingCommand] = {
            turnLeftCommand: CarHandlingCommand(movement="Left"),
            turnRightCommand: CarHandlingCommand(movement="Right"),
            driveCommand: CarHandlingCommand(movement="Forward"),
            reverseCommand: CarHandlingCommand(movement="Reverse"),
            stopCommand: CarHandlingCommand(movement="Stopped"),
            increaseSpeedCommand: CarHandlingCommand(speedChange=speedStep),
            decreaseSpeedCommand: CarHandlingCommand(speedChange=-speedStep)
        }

        for speed in range(0, 101):
            command = format_command(exactSpeedCommand_param, str(speed))
            newCommands.update({command: CarHandlingCommand(speedValue=speed)})

        return newCommands

    def get_honk_commands(self, honkCommands: dict[str: str], maxHonkTime: float) -> dict:
        self._check_for_placeholders_in_commands("honk_for_specified_time", honkCommands["honk_for_specified_time"])

        honkCommand = honkCommands["honk"]
        honkForSpecifiedTimeCommand_param = honkCommands["honk_for_specified_time"]

        allCommands: list[str] = [
            honkCommand,
            honkForSpecifiedTimeCommand_param
        ]

        self._check_for_duplicate_commands(allCommands, "HonkHandling")
        self._check_command_length(allCommands, "HonkHandling")

        newCommands: dict[str: HonkCommand] = {
            honkCommand: HonkCommand(singleHonk=True),
        }

        honkTime: float = 0.1
        stepValue: float = 0.1
        while honkTime <= (maxHonkTime + stepValue):
            command: str = format_command(honkForSpecifiedTimeCommand_param, str(round(honkTime, 1)))
            newCommands.update({command: HonkCommand(
                honkForDuration=round(honkTime, 1))})  # round honkTime to avoid floating numbers with many decimals

            honkTime += stepValue

        return newCommands

    def get_camera_servo_handling_commands(self, servoCommands: dict[str: str], minAngles: dict[str: int],
                                           maxAngles: dict[str: int]) -> dict:
        self._check_for_placeholders_in_commands("look_up_exact", servoCommands["look_up_exact"])
        self._check_for_placeholders_in_commands("look_down_exact", servoCommands["look_down_exact"])
        self._check_for_placeholders_in_commands("look_left_exact", servoCommands["look_left_exact"])
        self._check_for_placeholders_in_commands("look_right_exact", servoCommands["look_right_exact"])

        lookUpCommand = servoCommands["look_up"]
        lookDownCommand = servoCommands["look_down"]
        lookLeftCommand = servoCommands["look_left"]
        lookRightCommand = servoCommands["look_right"]
        lookCenterCommand = servoCommands["look_center"]

        lookUpExact = servoCommands["look_up_exact"]
        lookDownExact = servoCommands["look_down_exact"]
        lookLeftExact = servoCommands["look_left_exact"]
        lookRightExact = servoCommands["look_right_exact"]

        allCommands: list[str] = [
            lookDownCommand,
            lookUpCommand,
            lookLeftCommand,
            lookRightCommand,
            lookCenterCommand,
            lookUpExact,
            lookDownExact,
            lookLeftExact,
            lookRightExact
        ]

        self._check_command_length(allCommands, "CameraServoHandling")
        self._check_for_duplicate_commands(allCommands, "CameraServoHandling")

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
            self._get_angle_commands_for_given_plane(angleRange, command, plane)
        )

        # looking left commands
        plane: str = "horizontal"
        angleRange: range = range(1, maxAngles[plane] + 1)
        command: str = lookLeftExact
        newCommands.update(
            self._get_angle_commands_for_given_plane(angleRange, command, plane)
        )

        # looking down commands
        plane: str = "vertical"
        angleRange: range = range(minAngles[plane], 0)
        command: str = lookDownExact
        newCommands.update(
            self._get_angle_commands_for_given_plane(angleRange, command, plane)
        )

        # looking up commands
        plane: str = "vertical"
        angleRange: range = range(1, maxAngles[plane] + 1)
        command: str = lookUpExact
        newCommands.update(
            self._get_angle_commands_for_given_plane(angleRange, command, plane)
        )

        return newCommands

    def _get_angle_commands_for_given_plane(self, angleRange, command, plane) -> dict:
        exactAngleCommands: dict = {}

        for angle in angleRange:
            userCommand: str = format_command(command, str(abs(
                angle)))  # take the absolute value, because the user will always say a positive value
            if plane == "vertical":
                exactAngleCommands[userCommand] = CameraServoCommand(
                    verticalAngle=angle
                )
            elif plane == "horizontal":
                exactAngleCommands[userCommand] = CameraServoCommand(
                    horizontalAngle=angle
                )

        return exactAngleCommands

    def get_command_descriptions(self, commands: dict[str: str], descriptions: dict[str: str],
                                 placeHolderReplacement=None) -> dict[str: str]:
        # match the commands with their descriptions
        commandsToDescriptions: dict[str: str] = {commandValue: descValue for
                                                  (commandKey, commandValue, descKey, descValue) in
                                                  zip(commands.keys(), commands.values(), descriptions.keys(),
                                                      descriptions.values()) if commandKey == descKey}

        # replace the placeholders in the descriptions with the actual commands
        if placeHolderReplacement is not None:
            placeHolder = "param"
            commandsToDescriptions = {command.replace(placeHolder, placeHolderReplacement): description for
                                      (command, description) in commandsToDescriptions.items()}

        return commandsToDescriptions

    def get_camera_helper_commands(self, commands: dict[str: str], minZoomValue: float, maxZoomValue: float,
                                   stepValue: float) -> dict:
        self._check_for_placeholders_in_commands("zoom", commands["zoom"])

        turnOnDisplayCommand = commands["turn_on_display"]
        turnOffDisplayCommand = commands["turn_off_display"]

        zoomExactCommand_param = commands["zoom"]
        zoomInCommand = commands["zoom_in"]
        zoomOutCommand = commands["zoom_out"]

        allCommands: list[str] = [
            turnOnDisplayCommand,
            turnOffDisplayCommand,
            zoomInCommand,
            zoomOutCommand,
            zoomExactCommand_param
        ]

        self._check_for_duplicate_commands(allCommands, "CameraHelper")
        self._check_command_length(allCommands, "CameraHelper")

        newCommands: dict[str: CameraHelperCommand] = {
            turnOnDisplayCommand: CameraHelperCommand(displayActive=True),
            turnOffDisplayCommand: CameraHelperCommand(displayActive=False),
            zoomInCommand: CameraHelperCommand(zoomChange=stepValue),
            zoomOutCommand: CameraHelperCommand(zoomChange=-stepValue)
        }

        zoomValue: float = minZoomValue
        while zoomValue <= (maxZoomValue + stepValue):
            command: str = format_command(zoomExactCommand_param, str(round(zoomValue, 1)))
            newCommands.update({command: CameraHelperCommand(
                zoomValue=round(zoomValue, 1))})  # round zoomValue to avoid floating numbers with many decimals

            zoomValue += stepValue

        return newCommands

    def _check_for_placeholders_in_commands(self, commandKey: str, commandValue: str) -> None:
        placeholder = "{param}"
        if placeholder not in commandValue:  # any keys with paramkeys need to contain the placeholder
            raise InvalidCommandException(f"Command {commandKey} is missing the {{param}} placeholder")

    def _check_for_duplicate_commands(self, commands: list[str], module: str) -> None:
        commandsInUse: list[str] = []
        for command in commands:
            if command in commandsInUse:
                raise InvalidCommandException(f"Command {command} is used multiple times in module {module}")
            commandsInUse.append(command)

    def _check_command_length(self, commands: list[str], module: str) -> None:
        for command in commands:
            if len(command.split()) < 2:
                raise InvalidCommandException(
                    f"Command {command} is too short in module {module}. Command should be minimum two words")
