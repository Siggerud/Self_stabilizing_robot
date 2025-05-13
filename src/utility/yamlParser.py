import yaml
from os import path
from exceptions import YamlParseException
from typing import Any, Callable

def get_float(specs: dict, key: str) -> float:
    return _get_datatype(specs, key, float)

def get_int(specs: dict, key: str) -> int:
    return _get_datatype(specs, key, int)

def get_bool(specs: dict, key: str) -> bool:
    return _get_datatype(specs, key, bool)

def _get_datatype(specs: dict, key: str, datatype: Callable) -> Any:
    try:
        return datatype(specs[key])
    except KeyError:
        raise YamlParseException(f"Key {key} not found in YAML file")
    except ValueError:
        raise YamlParseException(f"Value for key {key} can't be converted to {datatype.__name__} value")

def get_yaml_contents_from_file(filepath: str) -> dict:
    _check_if_config_file_exists(filepath)

    with open(filepath, 'r') as stream:
        return yaml.safe_load(stream)

def _check_if_config_file_exists(filepath: str) -> None:
    if not path.isfile(filepath):
        raise YamlParseException(f"{filepath} not found")