from multiprocessing import Array, Pipe
from utility.yamlParser import get_yaml_content_from_file, get_bool
from typing import Optional
from os import path

class InterProcessCommunicationObjectLoader:
    def __init__(self, configDirPath: str):
        self._configDirPath = configDirPath

    def load_pipe_between_command_generator_and_command_handler(self) -> Optional[tuple[Pipe, Pipe]]:
        pipeReceiver, pipeSender = Pipe(duplex=False)

        return pipeReceiver, pipeSender

    def load_shared_array_between_camera_and_command_handler(self, cameraConfigFileName: str, carConfigFileName: str, servoConfigFileName: str) -> Optional[Array]:
        print(self._configDirPath)
        cameraSpecs = self._get_content_from_config_file(cameraConfigFileName)
        if not self._check_if_module_enabled(cameraSpecs):
            return None

        arrayList: list = []

        # zoom and hud should be initialized to 1.0
        arrayList[0] = 1.0
        arrayList[1] = 1.0

        carSpecs = self._get_content_from_config_file(carConfigFileName)
        if self._check_if_module_enabled(carSpecs):
            arrayList.append(0.0) # speed
            arrayList.append(0.0) # direction

        servoSpecs = self._get_content_from_config_file(servoConfigFileName)
        if self._check_if_module_enabled(servoSpecs):
            arrayList.append(0.0) # horizontal servo angle
            arrayList.append(0.0) # vertical servo angle

        return Array('d', arrayList)

    #TODO: move to helper class
    def _check_if_module_enabled(self, specs: dict) -> bool:
        return get_bool(specs, "enabled")

    # TODO: move to helper class
    def _get_content_from_config_file(self, configFileName: str) -> dict:
        absoluteFilePath: str = path.join(self._configDirPath, configFileName + '.yml')

        return get_yaml_content_from_file(absoluteFilePath)