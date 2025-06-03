from logging.handlers import QueueHandler
import logging
from multiprocessing import Process, Queue
from datetime import datetime
from robotController import RobotController
from utility.roboCarHelper import print_startup_error
import traceback

def print_error_message_and_exit(errorMessage):
    traceback.print_exc()
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
        message = queue.get()
        if message is None:
            break
        logger.handle(message)

if __name__ == "__main__":
    queue = Queue()

    # setup logger
    processName = "main"
    logger = logging.getLogger(processName)
    logger.addHandler(QueueHandler(queue))
    logger.setLevel(logging.DEBUG)

    # setup logger process to handle log messages from the queue
    logger_p = Process(target=logger_process, args=(queue,))
    logger_p.start()

    logger.info("Main process started.")

    # setup car controller
    try:
        carController = RobotController(queue)
    except Exception as e:
        print_error_message_and_exit(e)
    #TODO: add logging to main process
    #TODO: fix ability to use keyboard interrupts in main process
    # start car
    carController.start()

    logger.info("Main process finished.")

    # send None to stop logger process
    queue.put(None)
    logger_p.join()
