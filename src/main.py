from os import path

from exceptions import X11ForwardingException
from moduleLoader import ModuleLoader
from robotController import RobotController
from utility.roboCarHelper import print_startup_error
import traceback

def print_error_message_and_exit(errorMessage):
    traceback.print_exc()
    print_startup_error(errorMessage)
    exit()


if __name__ == "__main__":


    # setup car controller
    try:
        carController = RobotController()
    except X11ForwardingException as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()
