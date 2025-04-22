from abc import ABC, abstractmethod

class CommandRetriever(ABC):
    @abstractmethod
    def get_car_handling_commands(self, *args) -> dict:
        pass

    @abstractmethod
    def get_honk_commands(self, *args) -> dict:
        pass

    @abstractmethod
    def get_camera_servo_handling_commands(self, *args) -> dict:
        pass

    @abstractmethod
    def get_command_descriptions(self, *args) -> dict:
        pass

    @abstractmethod
    def get_camera_helper_commands(self, *args) -> dict:
        pass

