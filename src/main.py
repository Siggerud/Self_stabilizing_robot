from robotControl import RobotControl
from utility.roboCarHelper import print_startup_error
from moduleLoader import ModuleLoader
from exceptions import YamlParseException, X11ForwardingException
from xBoxEventHandler import XBoxEventHandler
from xboxControl import XboxControl

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

        # setup command handler
        commandHandler = moduleLoader.setup_command_handler(camera)

        #audioHandler = moduleLoader.setup_audio_handler()
        xboxControlHandler = moduleLoader.setup_xbox_handler()

        stabilizer = moduleLoader.setup_stabilizer()
    except YamlParseException as e:
        print_error_message_and_exit(e)

    # setup ipc between commandHandler and audioHandler
    #audioHandler.setup(commandHandler.pipeSender)
    xboxControlHandler.setup(commandHandler.pipeSender)

    # setup car controller
    try:
        carController = RobotControl(camera, commandHandler, xboxControlHandler, stabilizer)
    except X11ForwardingException as e:
        print_error_message_and_exit(e)

    # start car
    carController.start()
