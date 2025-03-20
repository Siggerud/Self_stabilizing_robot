from dataclasses import dataclass

@dataclass
class CameraHelperCommand:
    displayActive: bool
    zoomValue: float
    zoomChange: float