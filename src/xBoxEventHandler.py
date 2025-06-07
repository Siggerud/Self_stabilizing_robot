from commandGenerator import CommandGenerator
from xboxControl import XboxControl
from data.xBoxControlData import XBoxControlData
from time import sleep
from exceptions import XboxControlException
from typing import Optional
from multiprocessing import Pipe

class XBoxEventHandler(CommandGenerator):
    def __init__(self, xboxControl: XboxControl, exitCommand: str):
        self._xboxControl = xboxControl
        self._exitCommand: str = exitCommand
        self._set_controller()
        self._pushStateToWord: dict[int: str] = {
            0: "release",
            1: "press"
        }

        self._pipeSender: Optional[Pipe] = None

    def setup(self, pipeSender) -> None:
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        while not flag.value:
            #TODO: check every 10 seconcds of inactivity for xbox control connection

            controllerData = self._xboxControl.get_controller_data()
            command = self._process_controller_data_to_commands(controllerData)

            self._send_xbox_control_command_to_ipc(command)

            if self._exitCommand in command:
                flag.value = True

    def cleanup(self) -> None:
        self._xboxControl.cleanup()

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

    def _process_controller_data_to_commands(self, controllerData: XBoxControlData) -> str:
        return self._process_controller_data_to_command(controllerData)

    def _process_controller_data_to_command(self, data: XBoxControlData) -> Optional[str]:
        if data.pushButton is not None:
            return f"{data.pushButton} {self._pushStateToWord[data.pushState]}"
        elif data.stick is not None:
            return f"{data.stick} {round(data.stickValue, 2)}"