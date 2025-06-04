import logging
from datetime import datetime
from logging.handlers import QueueHandler
from multiprocessing import Queue
from os import path
from zoneinfo import ZoneInfo

from utility.yamlParser import get_yaml_content_from_file


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

    def logger_process(self, queue) -> None:
        logger = logging.getLogger('app')

        # Log to a file
        timezone = self._get_timezone("global")
        now = datetime.now(timezone)
        log_filename = f"logs/process_log_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        file_handler = logging.FileHandler(log_filename)

        formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
        formatter.converter = lambda *args: datetime.now(timezone).timetuple()
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

        while True:
            try:
                message = queue.get()
            except KeyboardInterrupt:
                continue  # if keyboard interrupt occurs, continue to retrieve the rest of the logs
            if message is None:
                break
            logger.handle(message)

    def _get_timezone(self, configFileName: str) -> ZoneInfo:
        loggingSpecs: dict = self._get_content_from_config_file(configFileName)

        return ZoneInfo(loggingSpecs["logging"]["timezone"])

    def _get_logging_level(self, configFileName: str, processName: str) -> int:
        loggingSpecs: dict = self._get_content_from_config_file(configFileName)

        return self._loggingLevelToNumericValue[loggingSpecs["logging"]["level"][processName].upper()]

    def _get_content_from_config_file(self, configFileName: str) -> dict:
        absoluteFilePath: str = path.join(self._configDirPath, configFileName + '.yml')

        return get_yaml_content_from_file(absoluteFilePath)
