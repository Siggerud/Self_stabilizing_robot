from commandGenerator import CommandGenerator
from xboxControl import XboxControl
from xBoxControlData import XBoxControlData
from roboCarHelper import round_to_nearest

class XBoxControlHandler(CommandGenerator):
    def __init__(self, xboxControl: XboxControl):
        self._xboxControl = xboxControl
        self._roundValue = 0.02
        self._pushStateToWord: dict[int: str] = {
            0: "release",
            1: "press"
        }

        self._pipeSender = None

    def setup(self, pipeSender) -> None:
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        print("Starting!")
        while not flag.value:
            print("now!")
            controllerData = self._xboxControl.get_controller_data()
            print(controllerData)
            commands = self._process_controller_data_to_commands(controllerData)
            for command in commands:
                print(command)
                self._send_xbox_control_command_to_ipc(command)

    def _send_xbox_control_command_to_ipc(self, command: str) -> None:
        # set the command in IPC
        self._pipeSender.send(command)

    def _process_controller_data_to_commands(self, controllerData: list[XBoxControlData]) -> list[str]:
        return [self._process_controller_data_to_command(data) for data in controllerData]

    def _process_controller_data_to_command(self, data: XBoxControlData) -> str:
        if data.pushButton is not None:
            return f"{data.pushButton} {self._pushStateToWord[data.pushState]}"
        elif data.stick is not None:
            return f"{data.stick} {round_to_nearest(data.stickValue, self._roundValue)}"

