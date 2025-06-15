from dataclasses import dataclass
from typing import Optional


@dataclass
class StabilizerInstruction:
    stabilize: Optional[bool] = None
