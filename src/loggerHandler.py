import logging
from logging.handlers import QueueHandler
from multiprocessing import Queue
from utility.yamlParser import get_yaml_content_from_file
from os import path

class LoggerHandler:
    def __init__(self, configDirPath: str):
        self._configDirPath = configDirPath
        self._loggingLevelToNumericValue = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

    def get_process_logger(self, configFileName: str, processName: str, queue: Queue) -> logging.Logger:
        logger = logging.getLogger(processName)
        logger.addHandler(QueueHandler(queue))
        logger.setLevel(self._get_logging_level(configFileName, processName))

        return logger

    def _get_logging_level(self, configFileName: str, processName: str) -> int:
        loggingSpecs: dict = self._get_content_from_config_file(configFileName)

        return self._loggingLevelToNumericValue[loggingSpecs["logging"]["level"][processName].upper()]

    def _get_content_from_config_file(self, configFileName: str) -> dict:
        absoluteFilePath: str = path.join(self._configDirPath, configFileName + '.yml')

        return get_yaml_content_from_file(absoluteFilePath)