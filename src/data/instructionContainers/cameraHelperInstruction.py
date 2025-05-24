from dataclasses import dataclass
from typing import Optional

@dataclass
class CameraHelperInstruction:
    displayActive: Optional[bool] = None
    changeDisplayActive: Optional[bool] = None
    zoomValue: Optional[float] = None
    zoomChange: Optional[float] = None