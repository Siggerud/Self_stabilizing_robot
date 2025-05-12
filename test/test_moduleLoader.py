import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, MagicMock
from os import path

@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")

@patch('moduleLoader.AudioHandler')
def test_setup_command_generator(mock_audio_handler, configDirPath):
    print(configDirPath)
    loader = ModuleLoader(configDirPath, "global")

    mock_audio_handler_instance = MagicMock()
    mock_audio_handler.return_value = mock_audio_handler_instance

    loader.setup_command_generator()

    assert mock_audio_handler.assert_called_once()
