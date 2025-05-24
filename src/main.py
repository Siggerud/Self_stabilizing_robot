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
    configDirPath = path.join(path.dirname(__file__), "config")

    # set up parser
    moduleLoader: ModuleLoader = ModuleLoader(configDirPath, "global")

    # setup modules
    try:
        # setup camera
        camera = moduleLoader.setup_camera("camera")

        # setup car
        car = moduleLoader.setup_car_handling("car_handling")

        # define servos aboard car
        servo = moduleLoader.setup_camera_servo_handling("servo")

        # setup honk
        honk = moduleLoader.setup_honk_handling("honk")

        # setup camera handler
        cameraHandler = moduleLoader.setup_camera_handler("camera")

        # setup signal lights
        signalLights = moduleLoader.setup_signal_lights("signal_lights")

        # setup command handler
        commandHandler = moduleLoader.setup_command_handler(camera, car, servo, cameraHandler, honk, signalLights)

        # setup command generator
        commandGenerator = moduleLoader.setup_command_generator()

        stabilizer = moduleLoader.setup_stabilizer("stabilizer")
    except Exception as e:
        print_error_message_and_exit(e)

    # setup ipc between commandHandler and audioHandler
    commandGenerator.setup(commandHandler.pipeSender)

    # setup car controller
    try:
        carController = RobotController(camera, commandHandler, commandGenerator, stabilizer)
    except X11ForwardingException as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()
