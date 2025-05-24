from commandGenerator import CommandGenerator
from sshkeyboard import listen_keyboard

class KeyboardEventHandler(CommandGenerator):
    def setup(self):
        pass

    def process_commands(self, flag) -> None:
        def press(key):
            print(f"'{key}' pressed")
            # (optional: set flag based on a keypress here too)

        def release(key):
            print(f"'{key}' released")

        def stop_condition():
            return flag.value

        # This blocks until stop_condition() returns True
        listen_keyboard(
            on_press=press,
            on_release=release,
            until=stop_condition
        )

        print("Stopping keyboard listener.")

    def cleanup(self) -> None:
        pass