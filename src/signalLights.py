import RPi.GPIO as GPIO
from time import sleep
from roboCarHelper import RobocarHelper

class SignalLights:
    def __init__(self, greenLightPin: int, yellowLightPin: int, redLightPin: int, blinkTime: float):
        self._check_argument_validity(blinkTime)

        self._lightPins: dict = {
            "green": greenLightPin,
            "yellow": yellowLightPin,
            "red": redLightPin
        }
        self._blinkTime: float = blinkTime

    @property
    def pins(self) -> list[int]:
        return list(self._lightPins.values())

    def setup(self) -> None:
        for pin in self._lightPins.values():
            GPIO.setup(pin, GPIO.OUT)

        # blink three times in rapid sucession to signal startup
        self._blink_all_lights()

    def cleanup(self) -> None:
        self._blink_all_lights() # blink to signal that class is shutting down

    def blink(self, color: str) -> None:
        pin: int = self._lightPins[color]

        # turn on light
        GPIO.output(pin, GPIO.HIGH)
        sleep(self._blinkTime)

        # turn off light
        GPIO.output(pin, GPIO.LOW)

    def _blink_all_lights(self) -> None:
        timeBetweenBlinks: float = 0.1
        for _ in range(3):
            # turn on lights
            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.HIGH)

            sleep(self._blinkTime)

            # turn off lights
            for pin in self._lightPins.values():
                GPIO.output(pin, GPIO.LOW)

            sleep(timeBetweenBlinks)

    def _check_argument_validity(self, blinkTime: float) -> None:
        RobocarHelper.check_if_num_is_in_interval(blinkTime, 0.1, 10, "blinkTime")


