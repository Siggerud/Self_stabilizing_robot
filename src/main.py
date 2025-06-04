from logging.handlers import QueueHandler
import logging
from multiprocessing import Process, Queue
from datetime import datetime
from robotController import RobotController
from utility.roboCarHelper import print_startup_error
from loggerHandler import LoggerHandler
from os import path

def print_error_message_and_exit(errorMessage):
    print_startup_error(errorMessage)
    exit()

def logger_process(queue):
    logger = logging.getLogger('app')

    # Log to a file
    log_filename = f"logs/process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    while True:
        try:
            message = queue.get()
        except KeyboardInterrupt:
            continue # if keyboard interrupt occurs, continue to retrieve the rest of the logs
        if message is None:
            break
        logger.handle(message)

if __name__ == "__main__":
    queue = Queue()

    # setup logger
    loggerHandler = LoggerHandler(path.join(path.dirname(__file__), "config"))
    # processName = "main"
    # logger = logging.getLogger(processName)
    # logger.addHandler(QueueHandler(queue))
    # logger.setLevel(logging.DEBUG)
    logger = loggerHandler.get_process_logger("global", "main", queue)

    # setup logger process to handle log messages from the queue
    logger_p = Process(target=logger_process, args=(queue,))
    logger_p.start()

    logger.info("Main process started.")

    # setup car controller
    try:
        carController = RobotController(queue)
    except Exception as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()

    logger.info("Main process finished.")

    # send None to stop logger process
    queue.put(None)
    logger_p.join()
