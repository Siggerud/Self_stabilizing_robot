from time import sleep

from led import LED
from roboCarHelper import check_if_num_is_in_interval


class SignalLights:
    def __init__(self, greenLightPin: int, yellowLightPin: int, redLightPin: int, blinkTime: float):
        self._check_argument_validity(blinkTime)
        self._pins = [greenLightPin, yellowLightPin, redLightPin]

        self._lightPins: dict = {
            "green": LED(greenLightPin),
            "yellow": LED(yellowLightPin),
            "red": LED(redLightPin)
        }
        self._blinkTime: float = blinkTime

    @property
    def pins(self) -> list[int]:
        return self._pins

    def setup(self) -> None:
        for led in self._lightPins.values():
            led.setup()

        # blink three times in rapid sucession to signal startup
        self._blink_all_lights()

    def cleanup(self) -> None:
        self._blink_all_lights()  # blink to signal that class is shutting down

    def blink(self, color: str) -> None:
        led: LED = self._lightPins[color]

        # turn on light
        led.turn_on()
        sleep(self._blinkTime)

        # turn off light
        led.turn_off()

    def _blink_all_lights(self) -> None:
        timeBetweenBlinks: float = 0.1
        for _ in range(3):
            # turn on lights
            for led in self._lightPins.values():
                led.turn_on()

            sleep(self._blinkTime)

            # turn off lights
            for led in self._lightPins.values():
                led.turn_off()

            sleep(timeBetweenBlinks)

    def _check_argument_validity(self, blinkTime: float) -> None:
        check_if_num_is_in_interval(blinkTime, 0.1, 10, "blinkTime")
