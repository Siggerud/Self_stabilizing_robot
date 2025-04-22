from dataclasses import dataclass
from typing import Optional

@dataclass
class CameraServoCommand:
    horizontalAngle: Optional[int] = None
    verticalAngle: Optional[int] = None