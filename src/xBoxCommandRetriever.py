from commandRetriever import CommandRetriever
from commandContainers.honkCommand import HonkCommand


#TODO: get everything from config files
class XBoxCommandRetriever(CommandRetriever):
    def get_honk_commands(self, *args) -> dict:
        return {"X press": HonkCommand(startContinuousHonk=True),
                "X release": HonkCommand(stopContinuousHonk=True)}

    def get_car_handling_commands(self, *args) -> dict:
        return {}

    def get_camera_servo_handling_commands(self, *args) -> dict:
        return {}

    def get_command_descriptions(self, *args) -> dict:
        return {}

    def get_camera_helper_commands(self, *args) -> dict:
        return {}