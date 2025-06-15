import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import patch, MagicMock
from loggerHandler import LoggerHandler
from os import path
from multiprocessing import Queue
import logging


@pytest.fixture
def configDirPath():
    return path.join(path.dirname(__file__), "config")


@patch('logging.getLogger')
def test_get_process_logger_fallback_level(mock_get_logger, configDirPath):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    loggerHandler = LoggerHandler(configDirPath)
    loggerHandler.get_process_logger("global", "command_handler", Queue)

    # there is an invalid level in the config, so it should fallback to INFO
    mock_logger.setLevel.assert_called_with(logging.INFO)


@patch('logging.getLogger')
def test_get_process_logger(mock_get_logger, configDirPath):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    loggerHandler = LoggerHandler(configDirPath)
    loggerHandler.get_process_logger("global_logging", "main", Queue)

    mock_logger.setLevel.assert_called_with(logging.ERROR)
