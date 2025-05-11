import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from moduleLoader import ModuleLoader
from audioHandler import AudioHandler
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def loader():
    return ModuleLoader()

@patch('moduleLoader.AudioHandler')
def test_setup_command_generator(loader, mock_audio_handler):
    # Arrange
    mock_audio_handler_instance = MagicMock()
    mock_audio_handler.return_value = mock_audio_handler_instance

    loader.setup_command_generator()

    assert mock_audio_handler.assert_called_once()
