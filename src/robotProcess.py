from abc import ABC, abstractmethod

class RobotProcess(ABC):
    @abstractmethod
    def setup(self):
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