import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
import pytest

@pytest.fixture
def loader():
    return ModuleLoader()

def test_setup_command_generator(loader):
    result = loader.setup_command_generator()

    assert isinstance(result, AudioHandler)
