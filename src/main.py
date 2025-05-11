from robotControl import RobotControl
from utility.roboCarHelper import print_startup_error
from moduleLoader import ModuleLoader
from exceptions import YamlParseException, X11ForwardingException

def print_error_message_and_exit(errorMessage):
    print_startup_error(errorMessage)
    exit()


if __name__ == "__main__":
    # set up parser
    moduleLoader: ModuleLoader = ModuleLoader()

    # setup modules
    try:
        # setup camera
        camera = moduleLoader.setup_camera()

        # setup car
        car = moduleLoader.setup_car_handling()

        # define servos aboard car
        servo = moduleLoader.setup_servo()
        print(servo)
        # setup honk
        honk = moduleLoader.setup_honk_handling()

        # setup camera handler
        cameraHandler = moduleLoader.setup_camera_handler()

        # setup command handler
        commandHandler = moduleLoader.setup_command_handler(camera, car, servo, cameraHandler, honk)

        # setup command generator
        commandGenerator = moduleLoader.setup_command_generator()

        stabilizer = moduleLoader.setup_stabilizer()
    except YamlParseException as e:
        print_error_message_and_exit(e)

    # setup ipc between commandHandler and audioHandler
    #audioHandler.setup(commandHandler.pipeSender)
    commandGenerator.setup(commandHandler.pipeSender)

    # setup car controller
    try:
        carController = RobotControl(camera, commandHandler, commandGenerator, stabilizer)
    except X11ForwardingException as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()
