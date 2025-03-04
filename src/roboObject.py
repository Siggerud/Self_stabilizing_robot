from abc import ABC, abstractmethod

class RoboObject(ABC):
    @abstractmethod
    def pins(self) -> list[int]:
        pass

    @abstractmethod
    def commands(self) -> list[str]:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def get_command_validity(self, command: str) -> str:
        pass

    @abstractmethod
    def print_commands(self) -> None:
        pass

    @abstractmethod
    def handle_command(self, command: str) -> None:
        pass
