from dataclasses import dataclass
from typing import Optional

@dataclass
class XBoxControlData:
    pushButton: Optional[str] = None
    pushState: Optional[bool] = None
    stick: Optional[str] = None
    stickValue: Optional[float] = None