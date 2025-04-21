from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message

import pygame
from xBoxControlData import XBoxControlData
from typing import Optional

class XboxControl:
    def __init__(self):
        pygame.init()

        self._controller = Optional[pygame.joystick.Joystick]
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
            3: "X",
            4: "Y",
            15: "Back",
            11: "Start",
            6: "LB",
            7: "RB"
        }

        self._pushButtonsStates: dict[str: int] = self._create_button_state_dict(self._pushButtons)

        self._eventTypeToButtonStates: dict[int: int] = {
            pygame.JOYBUTTONUP: 0,
            pygame.JOYBUTTONDOWN: 1
        }

    def get_controller_data(self) -> list[XBoxControlData]:
        print("before loop")
        while True:
            events = self._get_controller_events()
            if len(events) > 0:
                return [self._get_xbox_control_data(event) for event in events]

    def connect_controller(self) -> bool:
        pygame.joystick.quit()  # fully reset the module
        pygame.joystick.init()  # re-init to detect new devices

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            self._controller = pygame.joystick.Joystick(0)
            self._controller.init()
            return True

        return False

    def get_controller_name(self) -> str:
        return self._controller.get_name()

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
        else:
            result = XBoxControlData()

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






