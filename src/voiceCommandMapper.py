from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from data.commandContainers.cameraServoCommand import CameraServoCommand
from data.commandContainers.carHandlingCommands import CarHandlingCommand
from data.commandContainers.honkCommands import HonkCommand
from exceptions import InvalidCommandException
from utility.roboCarHelper import format_command
from utility.mapperHelper import check_for_duplicate_commands
from commandMapperBase import CommandMapperBase

class VoiceCommandMapper(CommandMapperBase):
    def get_exit_command(self, globalSpecs: dict) -> str:
        return globalSpecs["audio"]["commands"]["exit"]

    def get_car_handling_commands(self, carHandlingSpecs: dict) -> dict:
        commands: dict[str: str] = carHandlingSpecs["audio"]["commands"]

        self._check_for_placeholders_in_commands("exact_speed", commands["exact_speed"])

        turnLeftCommand = commands["turn_left"]
        turnRightCommand = commands["turn_right"]
        driveCommand = commands["drive"]
        reverseCommand = commands["reverse"]
        stopCommand = commands["stop"]

        increaseSpeedCommand = commands["increase_speed"]
        decreaseSpeedCommand = commands["decrease_speed"]
        exactSpeedCommand_param = commands["exact_speed"]

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

        check_for_duplicate_commands(allCommands, "CarHandling")
        self._check_command_length(allCommands, "CarHandling")

        speedIncrement: int = int(carHandlingSpecs["other"]["speed_step"])
        newCommands: dict[str: CarHandlingCommand] = {
            turnLeftCommand: CarHandlingCommand(movement="Left"),
            turnRightCommand: CarHandlingCommand(movement="Right"),
            driveCommand: CarHandlingCommand(movement="Forward"),
            reverseCommand: CarHandlingCommand(movement="Reverse"),
            stopCommand: CarHandlingCommand(movement="Stopped"),
            increaseSpeedCommand: CarHandlingCommand(speedChange=speedIncrement),
            decreaseSpeedCommand: CarHandlingCommand(speedChange=-speedIncrement)
        }

        for speed in range(0, 101):
            command = format_command(exactSpeedCommand_param, str(speed))
            newCommands.update({command: CarHandlingCommand(speedValue=speed)})

        return newCommands

    def get_honk_commands(self, honkSpecs: dict) -> dict:
        self._check_for_placeholders_in_commands("honk_for_specified_time", honkSpecs["audio"]["commands"]["honk_for_specified_time"])

        honkCommands = honkSpecs["audio"]["commands"]

        honkCommand = honkCommands["honk"]
        honkForSpecifiedTimeCommand_param = honkCommands["honk_for_specified_time"]

        allCommands: list[str] = [
            honkCommand,
            honkForSpecifiedTimeCommand_param
        ]

        check_for_duplicate_commands(allCommands, "HonkHandling")
        self._check_command_length(allCommands, "HonkHandling")

        newCommands: dict[str: HonkCommand] = {
            honkCommand: HonkCommand(singleHonk=True),
        }

        honkTime: float = 0.1
        stepValue: float = 0.1
        maxHonkTime: float = float(honkSpecs["honk_times"]["max_honk_time"])
        while honkTime <= maxHonkTime:
            command: str = format_command(honkForSpecifiedTimeCommand_param, str(round(honkTime, 1)))
            newCommands.update({command: HonkCommand(
                honkForDuration=round(honkTime, 1))})  # round honkTime to avoid floating numbers with many decimals

            honkTime = round(honkTime + stepValue, 1)

        return newCommands

    def get_camera_servo_handling_commands(self, servoSpecs: dict) -> dict:
        commands: dict = servoSpecs["audio"]["commands"]

        self._check_for_placeholders_in_commands("look_up_exact", commands["look_up_exact"])
        self._check_for_placeholders_in_commands("look_down_exact", commands["look_down_exact"])
        self._check_for_placeholders_in_commands("look_left_exact", commands["look_left_exact"])
        self._check_for_placeholders_in_commands("look_right_exact", commands["look_right_exact"])

        lookUpCommand = commands["look_up"]
        lookDownCommand = commands["look_down"]
        lookLeftCommand = commands["look_left"]
        lookRightCommand = commands["look_right"]
        lookCenterCommand = commands["look_center"]

        lookUpExact = commands["look_up_exact"]
        lookDownExact = commands["look_down_exact"]
        lookLeftExact = commands["look_left_exact"]
        lookRightExact = commands["look_right_exact"]

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
        check_for_duplicate_commands(allCommands, "CameraServoHandling")

        minAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["min_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["min_angle"]
        }

        maxAngles: dict[str: int] = {
            "horizontal": servoSpecs["angle_limits_horizontal"]["max_angle"],
            "vertical": servoSpecs["angle_limits_vertical"]["max_angle"]
        }

        newCommands: dict[str: CameraServoCommand] = {
            lookUpCommand: CameraServoCommand(verticalAngle=maxAngles["vertical"], horizontalAngle=0),
            lookDownCommand: CameraServoCommand(verticalAngle=minAngles["vertical"], horizontalAngle=0),
            lookLeftCommand: CameraServoCommand(horizontalAngle=maxAngles["horizontal"], verticalAngle=0),
            lookRightCommand: CameraServoCommand(horizontalAngle=minAngles["vertical"], verticalAngle=0),
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

    def get_command_descriptions(self, specs: dict) -> dict[str: str]:
        commands: dict[str: str] = specs["audio"]["commands"]
        descriptions: dict[str: str] = specs["audio"]["command_descriptions"]

        # match the commands with their descriptions
        commandsToDescriptions: dict[str: str] = {commandValue: descValue for
                                                  (commandKey, commandValue, descKey, descValue) in
                                                  zip(commands.keys(), commands.values(), descriptions.keys(),
                                                      descriptions.values()) if commandKey == descKey}

        # replace the placeholders in the descriptions with the actual commands if placeholder exists
        try:
            placeHolderReplacement: str = specs["audio"]["placeholder"]
            placeHolder: str = "param"
            commandsToDescriptions = {command.replace(placeHolder, placeHolderReplacement): description for
                                      (command, description) in commandsToDescriptions.items()}
        except KeyError:
            pass

        return commandsToDescriptions

    def get_camera_helper_commands(self, cameraSpecs: dict) -> dict:
        commands: dict = cameraSpecs["audio"]["commands"]

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

        check_for_duplicate_commands(allCommands, "CameraHandler")
        self._check_command_length(allCommands, "CameraHandler")

        maxZoomValue = float(cameraSpecs["zoom"]["max_zoom_value"])
        zoomIncrement = float(cameraSpecs["zoom"]["zoom_step"])

        newCommands: dict[str: CameraHelperCommand] = {
            turnOnDisplayCommand: CameraHelperCommand(displayActive=True),
            turnOffDisplayCommand: CameraHelperCommand(displayActive=False),
            zoomInCommand: CameraHelperCommand(zoomChange=zoomIncrement),
            zoomOutCommand: CameraHelperCommand(zoomChange=-zoomIncrement)
        }

        minZoomValue: float = 1.0
        zoomValue: float = minZoomValue
        while zoomValue <= maxZoomValue:
            command: str = format_command(zoomExactCommand_param, str(round(zoomValue, 1)))
            newCommands.update({command: CameraHelperCommand(
                zoomValue=round(zoomValue, 1))})  # round zoomValue to avoid floating numbers with many decimals

            zoomValue = round(zoomValue + zoomIncrement, 2)

        return newCommands

    def _check_for_placeholders_in_commands(self, commandKey: str, commandValue: str) -> None:
        placeholder = "{param}"
        if placeholder not in commandValue:  # any keys with paramkeys need to contain the placeholder
            raise InvalidCommandException(f"Command {commandKey} is missing the {{param}} placeholder")

    def _check_command_length(self, commands: list[str], module: str) -> None:
        for command in commands:
            if len(command.split()) < 2:
                raise InvalidCommandException(
                    f"Command {command} is too short in module {module}. Command should be minimum two words")
