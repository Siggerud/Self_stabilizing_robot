from dataclasses import dataclass
from typing import Optional

@dataclass
class CarHandlingCommand:
    movement: Optional[str] = None
    speedValue: Optional[int] = None
    speedChange: Optional[int] = None

    def __eq__(self, other):
        if isinstance(other, CarHandlingCommand):
            return (self.movement == other.movement and
                    self.speedChange == other.speedChange and
                    self.speedValue == other.speedValue)
        return False

    def __hash__(self):
        return hash((self.movement, self.speedChange, self.speedValue))