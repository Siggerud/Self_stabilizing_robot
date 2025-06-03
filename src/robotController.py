import subprocess
from multiprocessing import Process, Value, Array
from time import sleep
from utility.roboCarHelper import get_queue_logger
from os import path
import RPi.GPIO as GPIO
from data.raspberryPiPins import RaspberryPiPins
from exceptions import X11ForwardingException, InvalidPinException
from robotTask import RobotTask
from interProcessCommunicationObjectLoader import InterProcessCommunicationObjectLoader
from moduleLoader import ModuleLoader

class RobotController:
    def __init__(self, logger, loggerQueue) -> None:
        self._check_if_X11_connected()

        self._logger = logger
        self._logger = get_queue_logger(loggerQueue)
        #TODO: find another fix for this
        #self._validate_gpio_pins([commandHandler, stabilizer])
        self._configDirPath = path.join(path.dirname(__file__), "config")
        self._processes: list = []

        ipcLoader = InterProcessCommunicationObjectLoader(self._configDirPath)
        self.shared_array: Array = ipcLoader.load_shared_array_between_camera_and_command_handler("camera", "car_handling", "servo")
        self._pipeReceiver, self._pipeSender = ipcLoader.load_pipe_between_command_generator_and_command_handler()

        self.shared_flag = Value('b', False)

    def start(self) -> None:
        # start processes
        self._activate_camera()
        self._activate_command_handling()
        self._start_car_stabilization()

        # running this in main thread since I've had issues with running the audio handler in subprocesses
        self._start_generating_commands() # this is blocking

        # wait for all processes to finish
        self._cleanup()
        print("finished!")

    def _cleanup(self) -> None:
        # close all processes
        for process in self._processes:
            process.join()

    def _activate_camera(self) -> None:
        self._logger.info("Activating camera process...")
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _start_generating_commands(self) -> None:
        # setup command generator
        moduleLoader: ModuleLoader = ModuleLoader(self._configDirPath, "global")
        commandGenerator = moduleLoader.setup_command_generator()

        commandGenerator.setup(self._pipeSender)

        try:
            commandGenerator.process_commands(self.shared_flag)
        except KeyboardInterrupt:
            self.shared_flag.value = True  # set event to stop all active processes
        finally:
            # allow all processes to finish
            commandGenerator.cleanup()

    def _start_car_stabilization(self) -> None:
        process = Process(
            target=self._stabilize_car,
            args=(self.shared_flag,)
        )
        self._processes.append(process)
        process.start()

    def _activate_command_handling(self) -> None:
        process = Process(
            target=self._GPIO_Process,
            args=(self._start_listening_for_commands, self.shared_flag, self.shared_array, self._pipeReceiver)
        )
        self._processes.append(process)
        process.start()

    def _GPIO_Process(self, func, *args) -> None:
        GPIO.setmode(GPIO.BOARD)  # set GPIO mode as BOARD for all classes using GPIO pins
        GPIO.setwarnings(False)  # disable GPIO warnings
        func(*args)  # call parameter method
        GPIO.cleanup()  # cleanup all classes using GPIO pins

    def _stabilize_car(self, flag) -> None:
        moduleLoader: ModuleLoader = ModuleLoader(self._configDirPath, "global")
        stabilizer = moduleLoader.setup_stabilizer("stabilizer")
        if stabilizer is None:
            return

        stabilizer.setup()

        try:
            while not flag.value:
                stabilizer.stabilize()
        except KeyboardInterrupt:
            flag.value = True
        finally:
            stabilizer.cleanup()

    def _start_listening_for_commands(self, flag, shared_array, pipeReceiver) -> None:
        moduleLoader: ModuleLoader = ModuleLoader(self._configDirPath, "global")

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
        commandHandler = moduleLoader.setup_command_handler(car, servo, cameraHandler, honk, signalLights)

        commandHandler.setup(pipeReceiver)

        if commandHandler is None:
            return

        try:
            commandHandler.execute_commands(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            commandHandler.cleanup()

    def _start_camera(self, shared_array, flag) -> None:
        moduleLoader: ModuleLoader = ModuleLoader(self._configDirPath, "global")

        # setup camera
        camera = moduleLoader.setup_camera("camera", "car_handling", "servo")
        if camera is None:
            return

        camera.setup()

        try:
            camera.show_camera_feed(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            camera.cleanup()

    def _validate_gpio_pins(self, robotTasks: list[RobotTask]):
        for process in robotTasks:
            if process is not None:
                pins = process.gpio_pins
                self._check_if_pin_is_a_valid_pin_number(pins)
                self._check_if_pins_already_in_use(pins)

    def _check_if_pin_is_a_valid_pin_number(self, pins: list[int]) -> None:
        boardPins: tuple[int] = RaspberryPiPins().boardPins
        for pin in pins:
            # check that the pin number is a valid pin number
            if pin not in boardPins:
                raise InvalidPinException(f"Pin argument '{pin}' is not a valid pin number")

    def _check_if_pins_already_in_use(self, pins: list[int]) -> None:
        boardPinsInUse: list[int] = []
        for pin in pins:
            # check that pin has not already been specified by another robo object class
            if pin in boardPinsInUse:
                raise InvalidPinException(f"Pin {pin} is already in use")

            boardPinsInUse.append(pin)

    def _check_if_X11_connected(self) -> None:
        treshold: int = 5
        numOfTries: int = 0
        sleepTime: int = 5
        try:
            while numOfTries < treshold:
                result = subprocess.run(["xset", "q"], capture_output=True, text=True)
                returnCode: int = result.returncode
                numOfTries += 1
                if not returnCode:
                    print("Succesful connection to forwarded X11 server\n")
                    return
                else:
                    print(f"Failed to connect to X11 server. Trying again in {sleepTime} seconds...\n"
                          f"Number of retries: {treshold - numOfTries}\n")
                    sleep(sleepTime)
        except KeyboardInterrupt:
            raise X11ForwardingException("User aborted connecting to forwarded X11 server")

        raise X11ForwardingException("X11 forwarding not detected.")
