from abc import ABC, abstractmethod

# an object that can take a command and execute something based on that command
class CommandExecutors(ABC):
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
    def setup(self, *args) -> None:
        pass

    @abstractmethod
    def get_command_validity(self, command: str) -> str:
        pass

    @abstractmethod
    def handle_command(self, command: str) -> None:
        pass

    @abstractmethod
    def command_descriptions(self) -> dict[str: str]:
        pass

    @abstractmethod
    def __str__(self):
        pass
