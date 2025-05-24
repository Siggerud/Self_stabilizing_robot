from dataclasses import dataclass
from typing import Optional

@dataclass
class CameraServoInstruction:
    horizontalAngle: Optional[int] = None
    verticalAngle: Optional[int] = None