from abc import ABC, abstractmethod

class RobotTask(ABC):
    @abstractmethod
    def setup(self, *args):
        pass

    @abstractmethod
    def gpio_pins(self) -> list[int]:
        pass

    @abstractmethod
    def gpio_process(self) -> bool:
        pass

    @abstractmethod
    def cleanup(self):
        pass