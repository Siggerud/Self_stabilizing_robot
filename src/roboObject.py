from abc import ABC, abstractmethod

# an object that can take a command and execute something based on that command
class RoboObject(ABC):
    @abstractmethod
    def pins(self) -> list[int]:
        pass

    @abstractmethod
    def commands(self) -> dict[str: str]:
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
