from commandGenerator import CommandGenerator
from sshkeyboard import listen_keyboard, stop_listening
from multiprocessing import Pipe
from typing import Optional


class KeyboardEventHandler(CommandGenerator):
    def __init__(self, exitCommand: str):
        self._exitCommand: str = exitCommand
        self._pipeSender: Optional[Pipe] = None

    def setup(self, pipeSender):
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        def press(key):
            print(f"'{key}' pressed")
            command = key + "_pressed"
            self._pipeSender.send(command)

            if command == self._exitCommand:
                flag.value = True,
                stop_listening()

        def release(key):
            print(f"'{key}' released")
            command = key + "_released"
            self._pipeSender.send(command)

        # This blocks until stop_condition() returns True
        listen_keyboard(
            on_press=press,
            on_release=release,
            until=None
        )

        print("Stopping keyboard listener.")

    def cleanup(self) -> None:
        pass