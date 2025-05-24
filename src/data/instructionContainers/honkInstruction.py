from dataclasses import dataclass
from typing import Optional

@dataclass
class HonkInstruction:
    singleHonk: Optional[bool] = None
    honkForDuration: Optional[float] = None
    startContinuousHonk: Optional[bool] = None
    stopContinuousHonk: Optional[bool] = None