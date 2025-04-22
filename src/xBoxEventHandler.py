from commandGenerator import CommandGenerator
from xboxControl import XboxControl
from xBoxControlData import XBoxControlData
from utility.roboCarHelper import round_to_nearest
from time import sleep
from exceptions import XboxControlException
from typing import Optional
from multiprocessing import Pipe

class XBoxEventHandler(CommandGenerator):
    def __init__(self, xboxControl: XboxControl):
        self._xboxControl = xboxControl
        self._set_controller()
        #TODO: add roundvalue to config
        self._roundValue = 0.1
        self._pushStateToWord: dict[int: str] = {
            0: "release",
            1: "press"
        }

        self._pipeSender: Optional[Pipe] = None

    def setup(self, pipeSender) -> None:
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        while not flag.value:
            controllerData = self._xboxControl.get_controller_data()
            print(controllerData)
            commands = self._process_controller_data_to_commands(controllerData)
            for command in commands:
                print(command)
                self._send_xbox_control_command_to_ipc(command)

    def _set_controller(self) -> None:
        sleepTime: int = 10
        numOfTries: int = 0
        treshold: int = 5
        try:
            while numOfTries < treshold:
                connected = self._xboxControl.connect_controller()
                if connected:
                    print("Controller connected: ", self._xboxControl.get_controller_name())
                    return
                else:
                    numOfTries += 1

                    print(f"Xbox controller not connected. Trying again in {sleepTime} seconds...\n"
                          f"Number of retries: {treshold - numOfTries}\n")
                    sleep(sleepTime)
        except KeyboardInterrupt:
            raise XboxControlException("User aborted connecting xBox controller")

        raise XboxControlException("No xBox controller detected")

    def _send_xbox_control_command_to_ipc(self, command: str) -> None:
        # set the command in IPC
        self._pipeSender.send(command)

    def _process_controller_data_to_commands(self, controllerData: list[XBoxControlData]) -> list[str]:
        return [command for command in (self._process_controller_data_to_command(data) for data in controllerData) if command is not None]

    def _process_controller_data_to_command(self, data: XBoxControlData) -> Optional[str]:
        if data.pushButton is not None:
            return f"{data.pushButton} {self._pushStateToWord[data.pushState]}"
        elif data.stick is not None:
            return f"{data.stick} {round(round_to_nearest(data.stickValue, self._roundValue), 2)}" # could be many trailing zeroes, so round the number
