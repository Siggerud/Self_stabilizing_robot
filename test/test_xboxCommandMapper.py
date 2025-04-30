import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from exceptions import InvalidCommandException
from xBoxCommandMapper import XBoxCommandMapper

@pytest.fixture
def commandMapper():
    return XBoxCommandMapper()

@pytest.mark.parametrize("test_input", [
    {"xbox": {"commands": {"exit": "rt"}}},
{"xbox": {"commands": {"exit": "D-PAD up"}}},
{"xbox": {"commands": {"exit": "lsb"}}}
])
def test_push_button_validity_check(commandMapper, test_input):
    with pytest.raises(InvalidCommandException):
        commandMapper.get_exit_command(test_input)

def test_dpad_button_validity_check():
    pass
    #TODO

def test_sticks_validity_check():
    #TODO
    pass

def test_trigger_button_validity_check():
    #TODO
    pass