from commandMapperBase import CommandMapperBase
from data.commandContainers.honkCommands import HonkCommand
from data.commandContainers.cameraServoCommand import CameraServoCommand
from data.commandContainers.cameraHelperCommand import CameraHelperCommand
from data.commandContainers.carHandlingCommands import CarHandlingCommand
from utility.roboCarHelper import map_value_to_new_scale
from utility.mapperHelper import check_for_duplicate_commands
from exceptions import InvalidCommandException


class XBoxCommandMapper(CommandMapperBase):
    def get_exit_command(self, globalSpecs: dict) -> str:
        exitButton: str = globalSpecs["xbox"]["commands"]["exit"]
        self._check_if_push_buttons([exitButton], "Global")
        button = self._create_release_button(exitButton)
        return button

    def get_honk_commands(self, honkSpecs: dict) -> dict:
        honkCommands = honkSpecs["xbox"]["commands"]

        honkButton = honkCommands["honk"]
        self._check_if_push_buttons([honkButton], "HonkHandling")

        commands: dict[str: HonkCommand] = {
            self._create_press_button(honkButton): HonkCommand(startContinuousHonk=True),
            self._create_release_button(honkButton): HonkCommand(stopContinuousHonk=True)
        }
        print(commands)
        return commands

    def get_camera_servo_handling_commands(self, servoSpecs: dict) -> dict:
        # RSB stick
        servoCommands: dict = servoSpecs["xbox"]["commands"]

        servoSticks: dict[str: str] = {
            "horizontal": servoCommands["move_horizontal"],
            "vertical": servoCommands["move_vertical"]
        }
        self._check_if_sticks(list(servoSticks.values()), "CameraServoHandling")
        check_for_duplicate_commands(list(servoSticks.values()), "CameraServoHandling")

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
            if plane == "horizontal":
                instruction = CameraServoCommand(horizontalAngle=stickValueToAngle)
            elif plane == "vertical":
                instruction = CameraServoCommand(verticalAngle=stickValueToAngle)
            commands[f"{servoSticks[plane].upper()} {plane} {round(stickValue, 2)}"] = instruction

            stickValue += stepValue

        return commands

    def get_car_handling_commands(self, carHandlingSpecs: dict) -> dict:
        carHandlingCommands: dict[str: str] = carHandlingSpecs["xbox"]["commands"]

        driveTrigger: str = carHandlingCommands["drive"]
        reverseTrigger: str = carHandlingCommands["reverse"]
        self._check_if_trigger_buttons([driveTrigger, reverseTrigger], "CarHandling")
        check_for_duplicate_commands([reverseTrigger, driveTrigger], "CarHandling")

        turnStick: str = carHandlingCommands["turning"]
        self._check_if_sticks([turnStick], "CarHandling")

        commands: dict[str: CarHandlingCommand] = {}

        # generate commands for drive and reverse
        minStickValue: float = -1
        stickValue = minStickValue
        maxStickValue: float = 1
        stepValue = 0.01
        while stickValue <= maxStickValue:
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, -1, 1))
            commands[f"{driveTrigger.upper()} {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Forward")
            commands[f"{reverseTrigger.upper()} {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Reverse")

            stickValue += stepValue

        # generate commands for turning left
        stickValue = minStickValue
        while stickValue < 0: # from -1 to -0.01
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, 0, -1))
            commands[f"{turnStick.upper()} horizontal {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Left")

            stickValue += stepValue

        # generate command for when turning stick i centered
        commands[f"{turnStick.upper()} horizontal 0.0"] = CarHandlingCommand(speedValue=0, movement="Stopped")

        # generate commands for turning right
        stickValue = 0 + stepValue
        while stickValue <= 1: # from 0.01 to 1
            stickValueToSpeedValue = int(map_value_to_new_scale(stickValue, 0, 100, 0, 1))
            commands[f"{turnStick.upper()} horizontal {round(stickValue, 2)}"] = CarHandlingCommand(speedValue=stickValueToSpeedValue, movement="Right")

            stickValue += stepValue

        return commands

    def get_camera_helper_commands(self, cameraSpecs: dict) -> dict:
        cameraHelperCommands = cameraSpecs["xbox"]["commands"]

        displayButton: str = cameraHelperCommands["turn_display_on_or_off"]
        self._check_if_push_buttons([displayButton], "CameraHandler")

        zoomInButton: str = cameraHelperCommands["zoom_in"]
        zoomOutButton: str = cameraHelperCommands["zoom_out"]
        self._check_if_dpad_button([zoomInButton, zoomOutButton], "CameraHandler")
        check_for_duplicate_commands([zoomInButton, zoomOutButton], "CameraHandler")

        zoomIncrement = float(cameraSpecs["zoom"]["zoom_step"])

        commands: dict[str: CameraHelperCommand] = {
            self._create_press_button(displayButton): CameraHelperCommand(changeDisplayActive=True),
            self._create_press_button(zoomInButton): CameraHelperCommand(zoomChange=zoomIncrement),
            self._create_press_button(zoomOutButton): CameraHelperCommand(zoomChange=-zoomIncrement)
        }

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

    def _check_if_dpad_button(self, buttons: list[str], module: str) -> None:
        dpadButtons: list[str] = ["D-PAD up", "D-PAD down", "D-PAD left", "D-PAD right"]
        self._check_if_button_is_in_valid_list(buttons, dpadButtons, module, "dpad button")

    def _check_if_trigger_buttons(self, buttons: list[str], module: str) -> None:
        triggerButtons: list[str] = ["LT", "RT"]
        self._check_if_button_is_in_valid_list(buttons, triggerButtons, module, "trigger button")

    def _check_if_sticks(self, buttons: list[str], module: str) -> None:
        sticks: list[str] = ["LSB", "RSB"]
        self._check_if_button_is_in_valid_list(buttons, sticks, module, "stick")

    def _check_if_push_buttons(self, buttons: list[str], module: str) -> None:
        pushButtons: list[str] = ["A", "B", "X", "Y", "BACK", "START", "RB", "LB"]
        self._check_if_button_is_in_valid_list(buttons, pushButtons, module, "push button")

    def _check_if_button_is_in_valid_list(self, buttons: list[str], validList: list[str], module: str, buttonDescription: str) -> None:
        for button in buttons:
            if button.upper() not in validList:
                raise InvalidCommandException(f"Invalid button in module {module}. {button} is not a {buttonDescription}")

    def _create_press_button(self, button) -> str:
        return f"{button.upper} press"

    def _create_release_button(self, button) -> str:
        return f"{button.upper} release"
