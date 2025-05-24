from commandGenerator import CommandGenerator
from sshkeyboard import listen_keyboard
from multiprocessing import Pipe
from typing import Optional

class KeyboardEventHandler(CommandGenerator):
    def __init__(self):
        self._pipeSender: Optional[Pipe] = None

    def setup(self, pipeSender):
        self._pipeSender = pipeSender

    def process_commands(self, flag) -> None:
        def press(key):
            print(f"'{key}' pressed")
            command = key + "_pressed"
            self._pipeSender.send(key)

        def release(key):
            print(f"'{key}' released")
            command = key + "_released"
            self._pipeSender.send()

        # This blocks until stop_condition() returns True
        listen_keyboard(
            on_press=press,
            on_release=release
        )

        print("Stopping keyboard listener.")

    def cleanup(self) -> None:
        pass