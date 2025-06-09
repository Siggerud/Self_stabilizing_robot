import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
import pygame
from unittest.mock import patch
from xboxControl import XboxControl
from data.xBoxControlData import XBoxControlData


@pytest.mark.parametrize(
    "axis,value,expectedStick,expectedStickValue",
    [
        (0, 0.5394, "LSB horizontal", 0.5394),
        (3, -0.2917, "RSB vertical", -0.2917),
        (5, 0.9151, "LT", 0.9151)
    ]
)
@patch('xboxControl.pygame.event.wait')
@patch('xboxControl.pygame.init')
def test_get_controller_data_processing_of_events_for_sticks(mock_pygame_init, mock_pygame_event_wait, axis, value,
                                                             expectedStick, expectedStickValue):
    control = XboxControl()

    event = pygame.event.Event(
        pygame.JOYAXISMOTION,
        joy=0,  # Joystick ID (usually 0 if you have one joystick)
        axis=axis,  # Axis number
        value=value  # Axis value
    )
    mock_pygame_event_wait.return_value = event

    controlData = control.get_controller_data()

    assert controlData.stick == expectedStick
    assert controlData.stickValue == expectedStickValue


@pytest.mark.parametrize(
    "buttonEventType,buttonId,expectedButton,expectedButtonState",
    [
        (pygame.JOYBUTTONDOWN, 0, "A", 1),
        (pygame.JOYBUTTONUP, 3, "X", 0),
        (pygame.JOYBUTTONDOWN, 11, "START", 1)
    ]
)
@patch('xboxControl.pygame.event.wait')
@patch('xboxControl.pygame.init')
def test_get_controller_data_processing_of_events_for_push_buttons(mock_pygame_init, mock_pygame_event_wait,
                                                                   buttonEventType, buttonId, expectedButton,
                                                                   expectedButtonState):
    control = XboxControl()

    buttonEvent = pygame.event.Event(
        buttonEventType,
        joy=0,  # Joystick ID (usually 0)
        button=buttonId  # Button ID
    )
    mock_pygame_event_wait.return_value = buttonEvent

    controlData = control.get_controller_data()

    assert controlData.pushButton == expectedButton
    assert controlData.pushState == expectedButtonState

@pytest.mark.parametrize(
    "value,expectedButton",
    [
        ((1,0), "D-PAD RIGHT"),
        ((0, -1), "D-PAD DOWN")
    ]
)
@patch('xboxControl.pygame.event.wait')
@patch('xboxControl.pygame.init')
@patch('xboxControl.pygame.joystick')
def test_get_controller_data_processing_of_events_for_dpad_buttons_pushed(mock_pygame_joystick, mock_pygame_init, mock_pygame_event_wait,
                                                                   value, expectedButton):
    control = XboxControl()

    mock_pygame_joystick.get_count.return_value = 1
    control.connect_controller()

    mock_Joystick = mock_pygame_joystick.Joystick.return_value # mock controller
    mock_Joystick.get_hat.return_value = value

    buttonEvent = pygame.event.Event(
        pygame.JOYHATMOTION,
        joy=0,  # Joystick ID (usually 0)
        hat=0,  # Hat ID (usually 0 if there’s only one)
        value=value  # Tuple representing the hat position (x, y)
    )
    mock_pygame_event_wait.return_value = buttonEvent

    controlData = control.get_controller_data()

    assert controlData.pushButton == expectedButton
    assert controlData.pushState == 1

@pytest.mark.parametrize(
    "value,expectedButton",
    [
        ((-1,0), "D-PAD LEFT"),
        ((0, 1), "D-PAD UP")
    ]
)
@patch('xboxControl.pygame.event.wait')
@patch('xboxControl.pygame.init')
@patch('xboxControl.pygame.joystick')
def test_get_controller_data_processing_of_events_for_dpad_buttons_released(mock_pygame_joystick, mock_pygame_init, mock_pygame_event_wait,
                                                                   value, expectedButton):
    control = XboxControl()

    mock_pygame_joystick.get_count.return_value = 1
    control.connect_controller()

    mock_Joystick = mock_pygame_joystick.Joystick.return_value # mock controller
    mock_Joystick.get_hat.return_value = value

    buttonEventPressed = pygame.event.Event(
        pygame.JOYHATMOTION,
        joy=0,  # Joystick ID (usually 0)
        hat=0,  # Hat ID (usually 0 if there’s only one)
        value=value  # Tuple representing the hat position (x, y)
    )
    mock_pygame_event_wait.return_value = buttonEventPressed

    # first we call the method to register the buttons as pressed
    control.get_controller_data()

    buttonEventReleased = pygame.event.Event(
        pygame.JOYHATMOTION,
        joy=0,
        hat=0,
        value=(0,0 )  # value representing the hat position (x, y) when released
    )

    # mock the return of wait with the released event
    mock_pygame_event_wait.return_value = buttonEventReleased

    controlData = control.get_controller_data()

    assert controlData.pushButton == expectedButton
    assert controlData.pushState == 0