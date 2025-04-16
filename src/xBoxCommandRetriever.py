from commandRetriever import CommandRetriever
from commandContainers.honkCommand import HonkCommand

class XBoxCommandRetriever(CommandRetriever):
    def get_honk_commands(self, *args) -> dict:
        return {"X press": HonkCommand(singleHonk=True)}

    def get_car_handling_commands(self, *args) -> dict:
        return {}

    def get_camera_servo_handling_commands(self, *args) -> dict:
        return {}

    def get_command_descriptions(self, *args) -> dict:
        return {}

    def get_camera_helper_commands(self, *args) -> dict:
        return {}