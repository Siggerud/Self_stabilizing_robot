from raspberryPiPins import RaspberryPiPins
from exceptions import OutOfRangeException
from os import path

def get_full_file_path(self, filePath: str) -> str:
    return path.join(path.dirname(__file__), filePath)


def get_board_to_bcm_pins() -> None:
    piPins = RaspberryPiPins()
    return {boardPin: bcmPin for boardPin, bcmPin in zip(piPins.boardPins, piPins.bcmPins)}


def get_bcm_to_board_pins() -> None:
    piPins = RaspberryPiPins()
    return {bcmPin: boardPin for boardPin, bcmPin in zip(piPins.boardPins, piPins.bcmPins)}


def low_pass_filter(previousValue: float, currentValue: float, confidenceFactor:float=0.1) -> float:
    return previousValue * (1 - confidenceFactor) + currentValue * confidenceFactor


def map_value_to_new_scale(inputValue, newScaleMinValue, newScaleMaxValue, valuePrecision, oldScaleMinValue=-1,
                           oldScaleMaxValue=1) -> float:
    newScaleSpan = newScaleMaxValue - newScaleMinValue
    oldScaleSpan = oldScaleMaxValue - oldScaleMinValue

    valueScaled = float(inputValue - oldScaleMinValue) / float(oldScaleSpan)
    valueMapped = round(newScaleMinValue + (valueScaled * newScaleSpan), valuePrecision)

    return valueMapped


def check_if_num_is_in_interval(num: float, lowerBound: int, upperBound: int, variableName: str) -> None:
    if num < lowerBound or num > upperBound:
        raise OutOfRangeException(f"{variableName} should be between {lowerBound} and {upperBound}")


def check_if_num_is_greater_than_or_equal_to_number(num: float, lowerBound: int, variableName: str) -> None:
    if num <= lowerBound:
        raise OutOfRangeException(f"{variableName} should be greater than zero")


def format_command(command: str, param: str) -> str:
    return command.format(param=param)


def print_commands(title: str, dicts: dict[str, str]) -> None:
    maxCommandLength = max(len(command) for command in dicts.keys()) + 1

    print(title)
    for command, v in dicts.items():
        print(f"{command.ljust(maxCommandLength)}: {v['description']}")
    print()


def print_startup_error(error) -> None:
    print("Something went wrong during startup. Exiting...")
    print(error)




