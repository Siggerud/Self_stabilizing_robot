import RPi.GPIO as GPIO

class Buzzer:
    def __init__(self, buzzerPin: int) -> None:
        self._buzzerPin = buzzerPin

    def setup(self) -> None:
        GPIO.setup(self._buzzerPin, GPIO.OUT)

    def start_buzzing(self) -> None:
        GPIO.output(self._buzzerPin, GPIO.HIGH)

    def stop_buzzing(self) -> None:
        GPIO.output(self._buzzerPin, GPIO.LOW)
