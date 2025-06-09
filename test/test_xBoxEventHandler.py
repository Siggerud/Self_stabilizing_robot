import os
import sys
from multiprocessing import Value, Pipe

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import Mock, patch, call
from xBoxEventHandler import XBoxEventHandler
from data.xBoxControlData import XBoxControlData
from exceptions import XboxControlException

@patch('xBoxEventHandler.sleep')
def test_setting_of_controller_when_connected_after_some_tries(mock_sleep):
    mock_xbox_control = Mock()
    mock_xbox_control.connect_controller.side_effect = [False, False, True]

    XBoxEventHandler(mock_xbox_control, exitCommand="Back")

    expected_calls = [
        call(),
        call(),
        call()
    ]
    mock_xbox_control.connect_controller.assert_has_calls(expected_calls)

@patch('xBoxEventHandler.sleep')
def test_setting_of_controller_when_not_connected(mock_sleep):
    mock_xbox_control = Mock()
    mock_xbox_control.connect_controller.return_value = False

    with pytest.raises(XboxControlException):
        XBoxEventHandler(mock_xbox_control, exitCommand="Back")

    # check that connect_controller was called 5 times before it raised an exception
    expected_calls = [
        call(),
        call(),
        call(),
        call(),
        call()
    ]
    mock_xbox_control.connect_controller.assert_has_calls(expected_calls)

@pytest.mark.parametrize("controlData,expectedCommand", [
    (XBoxControlData(pushButton="A", pushState=1), "A press"),
    (XBoxControlData(pushButton="B", pushState=0), "B release"),
    (XBoxControlData(stick="RT", stickValue=-0.689343), "RT -0.69"),
    (XBoxControlData(pushButton="D-PAD DOWN", pushState=0), "D-PAD DOWN release")
])
def test_process_xbox_event_handler_sends_command(controlData, expectedCommand):
    mock_xbox_control = Mock()
    mock_xbox_control.get_controller_data.return_value = controlData

    handler = XBoxEventHandler(mock_xbox_control, exitCommand="Back")

    pipeReceiver, pipeSender = Pipe()
    handler.setup(pipeSender)

    flag = Value('b', False)

    # Patch flag.value to become True after one loop
    def set_flag_true(*args, **kwargs):
        flag.value = True
        return mock_xbox_control.get_controller_data.return_value

    mock_xbox_control.get_controller_data.side_effect = set_flag_true

    handler.process_commands(flag)

    #check that the command was sent through the pipe
    assert pipeReceiver.poll()
    assert pipeReceiver.recv() == expectedCommand

@pytest.mark.parametrize("button,expected_command", [
    ("A", "A press"),
    ("B", "B press"),
    ("X", "X press"),
    ("Y", "Y press"),
    ("Back", "Back press"),
    ("Start", "Start press"),
    ("LB", "LB press"),
    ("RB", "RB press")
])
def test_process_xbox_event_handler_exits_on_exit_command(button, expected_command):
    mock_xbox_control = Mock()
    mock_xbox_control.get_controller_data.return_value = XBoxControlData(pushButton=button, pushState=1)

    handler = XBoxEventHandler(mock_xbox_control, exitCommand=button)

    pipeReceiver, pipeSender = Pipe()
    handler.setup(pipeSender)

    flag = Value('b', False)

    # Run the command processing loop
    handler.process_commands(flag)

    # Check that the flag was set to True to indicate exit
    assert flag.value

    # check that the command was passed down the pipe
    assert pipeReceiver.poll()
    assert pipeReceiver.recv() == expected_command