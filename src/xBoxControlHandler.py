from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message

import pygame
from commandGenerator import CommandGenerator
from xboxControl import XboxControl
from xBoxControlData import XBoxControlData
from time import sleep
from exceptions import XboxControlException
from roboCarHelper import round_to_nearest

class XBoxControlHandler(CommandGenerator):
    def __init__(self, xboxControl: XboxControl):
        pygame.init()
        self._controller = self._get_controller()

        self._xboxControl = xboxControl
        self._roundValue = 0.02

        self._pipeSender = None

    def setup(self, pipeSender) -> None:
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        while not flag.value:
            controllerData = self._xboxControl.get_controller_data(self._controller)

            commands = self._process_controller_data_to_commands(controllerData)
            for command in commands:
                self._send_xbox_control_command_to_ipc(command)

    def _send_xbox_control_command_to_ipc(self, command: str) -> None:
        # set the command in IPC
        self._pipeSender.send(command)

    def _process_controller_data_to_commands(self, controllerData: list[XBoxControlData]) -> list[str]:
        return [self._process_controller_data_to_command(data) for data in controllerData]

    def _process_controller_data_to_command(self, data: XBoxControlData) -> str:
        if data.pushButton is not None:
            return f"{data.pushButton} {bool(data.pushState)}"
        elif data.stick is not None:
            return f"{data.stick} {round_to_nearest(data.stickValue, self._roundValue)}"

    def _get_controller(self) -> pygame.joystick.JoystickType:
        pygame.joystick.init()

        sleepTime: int = 10
        numOfTries: int = 0
        treshold: int = 5
        try:
            while numOfTries < treshold:
                num_joysticks = pygame.joystick.get_count()
                if num_joysticks == 0:
                    numOfTries += 1

                    print(f"Xbox controller not connected. Trying again in {sleepTime} seconds...\n"
                          f"Number of retries: {treshold - numOfTries}\n")
                    sleep(sleepTime)
                else:
                    controller = pygame.joystick.Joystick(0)
                    controller.init()
                    print("Controller connected: ", controller.get_name())
                    return controller
        except KeyboardInterrupt:
            raise XboxControlException("User aborted connecting xBox controller")

        raise XboxControlException("No xBox controller detected")