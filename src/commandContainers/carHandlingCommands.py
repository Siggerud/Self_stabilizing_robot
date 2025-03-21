from dataclasses import dataclass
from typing import Optional

@dataclass
class CarHandlingCommand:
    movement: Optional[str] = None
    speedValue: Optional[int] = None
    speedChange: Optional[int] = None