import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, MagicMock
from exceptions import YamlParseException
from os import path

@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")

@pytest.fixture
def xboxLoader(configDirPath):
    return ModuleLoader(configDirPath, "global_xbox")

@patch('moduleLoader.AudioHandler')
def test_setup_command_generator_audio(mock_audio_handler, configDirPath):
    loader = ModuleLoader(configDirPath, "global_audio")

    loader.setup_command_generator()

    mock_audio_handler.assert_called_once()

@patch('moduleLoader.XBoxEventHandler')
def test_setup_command_generator_xbox(mock_xbox_handler, configDirPath):
    loader = ModuleLoader(configDirPath, "global_xbox")

    loader.setup_command_generator()

    mock_xbox_handler.assert_called_once()

def test_error_handling_of_invalid_config_files(xboxLoader):
    with pytest.raises(YamlParseException):
        xboxLoader.setup_car_handling("car_racing")
