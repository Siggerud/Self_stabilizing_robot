from commandGenerator import CommandGenerator
from sshkeyboard import listen_keyboard
from time import sleep
from threading import Thread

class KeyboardEventHandler(CommandGenerator):
    def setup(self):
        pass

    def process_commands(self, flag) -> None:
        def press(key):
            print(f"'{key}' pressed")
            # (optional: set flag based on a keypress here too)

        def release(key):
            print(f"'{key}' released")

        def run():
            listen_keyboard(on_press=press, on_release=release)

        # Run listener in a thread because listen_keyboard is blocking
        t = Thread(target=run, daemon=True)
        t.start()

        while not flag.value:
            sleep(0.1)

        print("Stopping keyboard listener.")

    def cleanup(self) -> None:
        pass