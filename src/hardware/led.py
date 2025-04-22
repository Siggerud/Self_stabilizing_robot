import RPi.GPIO as GPIO

class LED:
    def __init__(self, ledPin: int) -> None:
        self._ledPin = ledPin

    def setup(self) -> None:
        GPIO.setup(self._ledPin, GPIO.OUT)

    def turn_on(self) -> None:
        GPIO.output(self._ledPin, GPIO.HIGH)

    def turn_off(self) -> None:
        GPIO.output(self._ledPin, GPIO.LOW)