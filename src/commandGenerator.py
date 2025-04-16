from abc import ABC, abstractmethod

# an object that can take a command and execute something based on that command
class CommandGenerator(ABC):
    @abstractmethod
    def setup(self, *args) -> None:
        pass

    @abstractmethod
    def process_commands(self, *args) -> None:
        pass