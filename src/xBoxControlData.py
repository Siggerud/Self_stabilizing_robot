from dataclasses import dataclass
from typing import Optional

@dataclass
class XBoxControlData:
    pushButton: Optional[str] = None
    pushState: Optional[int] = None
    stick: Optional[str] = None
    stickValue: Optional[float] = None