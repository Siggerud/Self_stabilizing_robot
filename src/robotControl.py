import subprocess
from multiprocessing import Process, Array, Value
from time import sleep
import RPi.GPIO as GPIO
from camera import Camera
from commandGenerator import CommandGenerator
from commandHandler import CommandHandler
from data.raspberryPiPins import RaspberryPiPins
from exceptions import X11ForwardingException, InvalidPinException
from robotProcess import RobotProcess
from stabilizer import Stabilizer
from typing import Optional


class RobotControl:
    def __init__(self, camera, commandHandler, commandGenerator, stabilizer):
        self._check_if_X11_connected()

        self._validate_gpio_pins([commandHandler, stabilizer])

        self._camera: Optional[Camera] = camera
        self._commandHandler: Optional[CommandHandler] = commandHandler
        self._commandGenerator: CommandGenerator = commandGenerator
        self._stabilizer: Optional[Stabilizer] = stabilizer

        self._processes: list = []

        self.shared_array = self._get_shared_array()

        self.shared_flag = Value('b', False)

    def start(self) -> None:
        # start processes
        self._activate_camera()
        self._activate_command_handling()
        self._start_car_stabilization()

        # running this in main thread since I've had issues with running the audio handler in subprocesses
        try:
            self._commandGenerator.process_commands(self.shared_flag)
        except KeyboardInterrupt:
            self.shared_flag.value = True  # set event to stop all active processes
        finally:
            # allow all processes to finish
            self._commandGenerator.cleanup()
            self._cleanup()
            print("finished!")

    def _cleanup(self) -> None:
        # close all processes
        for process in self._processes:
            process.join()

    # TODO: move this to setup file?
    def _get_shared_array(self) -> Optional[Array]:
        if self._camera is None:
            return None

        sharedArrayDict: dict = self._camera.array_dict

        # initialize the array list with the same size as the dict that corresponds to the array
        arrayList: list = [0.0] * len(sharedArrayDict.keys())

        # zoom and hud should be initialized to 1.0
        arrayList[sharedArrayDict["HUD"]] = 1.0
        arrayList[sharedArrayDict["Zoom"]] = 1.0

        return Array('d', arrayList)

    def _activate_camera(self) -> None:
        if self._camera is None:
            return

        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def _start_car_stabilization(self) -> None:
        if self._stabilizer is None:
            return

        process = Process(
            target=self._stabilize_car,
            args=(self.shared_flag,)
        )
        self._processes.append(process)
        process.start()

    def _activate_command_handling(self) -> None:
        if self._commandHandler is None:
            return

        process = Process(
            target=self._GPIO_Process,
            args=(self._start_listening_for_voice_commands, self.shared_flag, self.shared_array)
        )
        self._processes.append(process)
        process.start()

    def _GPIO_Process(self, func, *args) -> None:
        GPIO.setmode(GPIO.BOARD)  # set GPIO mode as BOARD for all classes using GPIO pins
        GPIO.setwarnings(False)  # disable GPIO warnings
        func(*args)  # call parameter method
        GPIO.cleanup()  # cleanup all classes using GPIO pins

    def _stabilize_car(self, flag) -> None:
        self._stabilizer.setup()

        try:
            while not flag.value:
                self._stabilizer.stabilize()
        except KeyboardInterrupt:
            flag.value = True
        finally:
            self._stabilizer.cleanup()

    def _start_listening_for_voice_commands(self, flag, shared_array) -> None:
        self._commandHandler.setup()

        try:
            self._commandHandler.execute_commands(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            self._commandHandler.cleanup()

    def _start_camera(self, shared_array, flag) -> None:
        self._camera.setup()

        try:
            self._camera.show_camera_feed(flag, shared_array)
        except KeyboardInterrupt:
            flag.value = True
        finally:
            self._camera.cleanup()

    def _validate_gpio_pins(self, robotProcesses: list[RobotProcess]):
        for process in robotProcesses:
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
