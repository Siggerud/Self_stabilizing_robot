from dataclasses import dataclass
from typing import Optional

@dataclass
class HonkCommand:
    singleHonk: Optional[bool] = None
    honkForDuration: Optional[float] = None