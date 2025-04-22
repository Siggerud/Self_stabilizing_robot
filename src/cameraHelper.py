class CameraHelper:
    def __init__(self, cameraHandler, car=None, servo=None):
        self._cameraHandler = cameraHandler
        self._car = car
        self._servo = servo

        self._directionValue_to_number: dict = {
            "Stopped": 0,
            "Left": 1,
            "Right": 2,
            "Forward": 3,
            "Reverse": 4
        }

        self._arrayDict: dict[str: int] = None

    def update_control_values_for_video_feed(self, shared_array) -> None:
        if self._servo:
            shared_array[self._arrayDict["horizontal servo"]] = self._servo.get_current_servo_angle("horizontal")
            shared_array[self._arrayDict["vertical servo"]] = self._servo.get_current_servo_angle("vertical")

        if self._car:
            shared_array[self._arrayDict["speed"]] = self._car.current_speed
            shared_array[self._arrayDict["direction"]] = self._directionValue_to_number[self._car.current_turn_value]

        shared_array[self._arrayDict["HUD"]] = float(self._cameraHandler.hudValue)
        shared_array[self._arrayDict["Zoom"]] = self._cameraHandler.zoomValue

    def set_array_dict(self, arrayDict: dict[str: int]) -> None:
        self._arrayDict = arrayDict
