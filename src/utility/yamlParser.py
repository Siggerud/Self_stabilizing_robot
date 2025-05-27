import yaml
from os import path
from exceptions import YamlParseException
from typing import Any, Callable

def get_float(specs: dict, key: str) -> float:
    # we don't want to convert bool values to float from the yaml files
    if isinstance(specs[key], bool):
        raise YamlParseException(f"Erroneous value '{specs[key]}' given for {key}")

    return _get_datatype(specs, key, float)

def get_int(specs: dict, key: str) -> int:
    # we don't want to convert bool values to ints from the yaml files
    if isinstance(specs[key], bool):
        raise YamlParseException(f"Erroneous value '{specs[key]}' given for {key}")

    return _get_datatype(specs, key, int)

def get_bool(specs: dict, key: str) -> bool:
    try:
        value = specs[key]
    except KeyError:
        raise YamlParseException(f"Key {key} not found in YAML file")
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise YamlParseException(f"Can't convert {value} to bool")


def _get_datatype(specs: dict, key: str, datatype: Callable) -> Any:
    try:
        return datatype(specs[key])
    except KeyError:
        raise YamlParseException(f"Key {key} not found in YAML file")
    except ValueError:
        raise YamlParseException(f"Value for key {key} can't be converted to {datatype.__name__} value")

def get_yaml_content_from_file(filepath: str) -> dict:
    _check_if_config_file_exists(filepath)

    with open(filepath, 'r') as stream:
        return yaml.safe_load(stream)

def _check_if_config_file_exists(filepath: str) -> None:
    if not path.isfile(filepath):
        print(filepath)
        raise YamlParseException(f"{filepath} not found")