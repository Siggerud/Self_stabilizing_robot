from dataclasses import dataclass

@dataclass
class RaspberryPiPins:
    boardPins: tuple[int] = (3, 5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40)
    bcmPins: tuple[int] = (2, 3, 4, 17, 18, 27, 22, 23, 24, 10, 9, 25, 11, 8, 7, 5, 6, 12, 13, 19, 16, 26, 20, 21)
