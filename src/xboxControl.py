from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message

import pygame
from commandGenerator import CommandGenerator
from time import sleep
from exceptions import XboxControlException
from xBoxControlData import XBoxControlData

class XboxControl(CommandGenerator):
    def __init__(self):
        pygame.init()
        self._controller = self._get_controller()

    def setup(self):
        pass

    def process_command(self, flag) -> None:
        while not flag.value:
            events = self._get_controller_events()
            if len(events) > 0:
                for event in events:
                    controlData = self._get_xbox_control_data(event)

    def _get_xbox_control_data(self, event):
        button = None
        buttonPressValue = None

        eventType = event.type
        if eventType == pygame.JOYHATMOTION:
            button = self._get_dpad_button(self._controller.get_hat(self._hatNum)[0])
            buttonPressValue = self._dpad_button_states[button]
        elif eventType == pygame.JOYAXISMOTION:
            axis = event.axis
            button = self._joyAxisMotionToButtons[axis]
            buttonPressValue = self.round_nearest(event.value, 0.02)
        elif eventType == pygame.JOYBUTTONDOWN or eventType == pygame.JOYBUTTONUP:
            button = self._get_pushed_button(event)
            buttonPressValue = self._pushButtonsStates[button]

        return button, buttonPressValue

    def _get_controller_events(self) -> list[pygame.event]:
        return pygame.event.get()

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

