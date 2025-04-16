from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message

import pygame
from xBoxControlData import XBoxControlData
from time import sleep
from exceptions import XboxControlException

class XboxControl:
    def __init__(self):
        pygame.init()
        self._controller = self._get_controller()
        self._hatNum = 0

        self._horizontalHatToButtons = {
            -1: "D-PAD left",
            1: "D-PAD right"
        }

        self._joyAxisMotionToButtons = {
            0: "LSB horizontal",
            1: "LSB vertical",
            2: "RSB horizontal",
            3: "RSB vertical",
            4: "RT",
            5: "LT",
        }

        self._dpad_button_states: dict[str: int] = self._create_button_state_dict(self._horizontalHatToButtons)

        self._pushButtons: dict[int: str] = {
            0: "A",
            1: "B",
            2: "X",
            3: "Y",
            4: "LB",
            5: "RB",
            7: "Start",
            6: "Back"
        }

        self._pushButtonsStates: dict[str: int] = self._create_button_state_dict(self._pushButtons)

        self._eventTypeToButtonStates: dict[int: int] = {
            pygame.JOYBUTTONUP: 0,
            pygame.JOYBUTTONDOWN: 1
        }

    def get_controller_data(self) -> list[XBoxControlData]:
        print("before loop")
        while True:
            print("after loop")
            events = self._get_controller_events()
            if len(events) > 0:
                return [self._get_xbox_control_data(event) for event in events]

    def _get_xbox_control_data(self, event) -> XBoxControlData:
        eventType = event.type
        if eventType == pygame.JOYHATMOTION:
            button = self._get_dpad_button(self._controller.get_hat(self._hatNum)[0])
            pushState = self._dpad_button_states[button]

            result = XBoxControlData(pushButton=button, pushState=pushState)
        elif eventType == pygame.JOYAXISMOTION:
            axis = event.axis
            stick = self._joyAxisMotionToButtons[axis]
            stickValue = event.value

            result = XBoxControlData(stick=stick, stickValue=stickValue)
        elif eventType == pygame.JOYBUTTONDOWN or eventType == pygame.JOYBUTTONUP:
            button = self._get_pushed_button(event)
            pushState = self._pushButtonsStates[button]

            result = XBoxControlData(pushButton=button, pushState=pushState)

        return result

    def _get_dpad_button(self, num) -> str:
        try:
            button = self._horizontalHatToButtons[num]
            self._dpad_button_states[button] = 1
        except KeyError:
            self._set_all_dpad_buttons_to_false()
        #TODO: need to account for vertical dpad pushes as well
        return button

    def _get_pushed_button(self, event) -> str:
        buttonNum = event.button
        button = self._pushButtons[buttonNum]

        self._update_push_state(button, event)

        return button

    def _update_dpad_state(self, button: str, state: int) -> None:
        self._dpad_button_states[button] = state

    def _update_push_state(self, button: str, event: pygame.event) -> None:
        self._pushButtonsStates[button] = self._eventTypeToButtonStates[event.type]

    def _create_button_state_dict(self, otherDict):
        buttonStateDict = {}
        for button in list(otherDict.values()):
            buttonStateDict[button] = 0

        return buttonStateDict

    def _set_all_dpad_buttons_to_false(self) -> None:
        for button in list(self._horizontalHatToButtons.values()):
            if self._dpad_button_states[button]:
                self._dpad_button_states[button] = 0
                break

    def _get_controller_events(self) -> list[pygame.event]:
        return pygame.event.get()

    def _get_controller(self) -> pygame.joystick.JoystickType:
        sleepTime: int = 10
        numOfTries: int = 0
        treshold: int = 5
        try:
            while numOfTries < treshold:
                pygame.joystick.init()
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



