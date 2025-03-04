from raspberryPiPins import RaspberryPiPins
from exceptions import OutOfRangeException

class RobocarHelper:
    def __init__(self):
        pass

    @staticmethod
    def get_board_to_bcm_pins():
        piPins = RaspberryPiPins()
        return {boardPin: bcmPin for boardPin, bcmPin in zip(piPins.boardPins, piPins.bcmPins)}

    @staticmethod
    def get_bcm_to_board_pins():
        piPins = RaspberryPiPins()
        return {bcmPin: boardPin for boardPin, bcmPin in zip(piPins.boardPins, piPins.bcmPins)}

    @staticmethod
    def low_pass_filter(previousValue: float, currentValue: float, confidenceFactor:float=0.1) -> float:
        return previousValue * (1 - confidenceFactor) + currentValue * confidenceFactor

    @staticmethod
    def map_value_to_new_scale(inputValue, newScaleMinValue, newScaleMaxValue, valuePrecision, oldScaleMinValue=-1,
                               oldScaleMaxValue=1) -> float:
        newScaleSpan = newScaleMaxValue - newScaleMinValue
        oldScaleSpan = oldScaleMaxValue - oldScaleMinValue

        valueScaled = float(inputValue - oldScaleMinValue) / float(oldScaleSpan)
        valueMapped = round(newScaleMinValue + (valueScaled * newScaleSpan), valuePrecision)

        return valueMapped

    @staticmethod
    def chain_together_dict_keys(dicts: list[dict]) -> list[str]:
        combinedKeys: list = []
        for dict in dicts:
            combinedKeys.extend(list(dict.keys()))

        return combinedKeys

    @staticmethod
    def check_if_num_is_in_interval(num: int, lowerBound: int, upperBound: int, variableName: str) -> None:
        if num < lowerBound or num > upperBound:
            raise OutOfRangeException(f"{variableName} should be between {lowerBound} and {upperBound}")

    @staticmethod
    def check_if_num_is_greater_than_or_equal_to_number(num: int, lowerBound: int, variableName: str) -> None:
        if num <= lowerBound:
            raise OutOfRangeException(f"{variableName} should be greater than zero")

    @staticmethod
    def format_command(command: str, param: str) -> str:
        return command.format(param=param)

    @staticmethod
    def print_commands(title: str, dicts: dict[str, str]) -> None:
        maxCommandLength = max(len(command) for command in dicts.keys()) + 1

        print(title)
        for command, v in dicts.items():
            print(f"{command.ljust(maxCommandLength)}: {v['description']}")
        print()

    @staticmethod
    def print_startup_error(error) -> None:
        print("Something went wrong during startup. Exiting...")
        print(error)

    @staticmethod
    def round_nearest(x, a) -> float:
        return round(x / a) * a



