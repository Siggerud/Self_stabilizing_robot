from multiprocessing import Queue
from robotController import RobotController
from utility.roboCarHelper import print_startup_error
from loggerHandler import LoggerHandler
from os import path
import sys
from typing import Optional


def print_error_message_and_exit(errorMessage):
    print_startup_error(errorMessage)
    exit()


def get_user_controller() -> Optional[str]:
    if len(sys.argv) == 2:
        return sys.argv[1].lower()
    elif len(sys.argv) == 1:
        return None
    else:
        raise ValueError("Too many command line arguments provided. Expected max one argument for controller type.")


if __name__ == "__main__":
    queue = Queue()

    # setup logger
    loggerHandler = LoggerHandler(path.join(path.dirname(__file__), "config"))
    logger = loggerHandler.get_process_logger("global", "main", queue)

    # setup logger process to handle log messages from the queue
    loggerHandler.start_logger_process(queue)

    logger.info("Main process started.")

    # setup car controller
    try:
        userController = get_user_controller()
        carController = RobotController(queue, userController)
    except Exception as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()

    logger.info("Main process finished.")

    # stop logger process
    loggerHandler.stop_logger_process()
