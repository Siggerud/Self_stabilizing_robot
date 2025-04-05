import RPi.GPIO as GPIO
from roboCarHelper import map_value_to_new_scale, check_if_num_is_in_interval

class MotorDriver:
    def __init__(self,
                 pins: dict[str: int],
                 motorInfo: dict,
                 pwm: dict[str: int]
                 ):
        #TODO: validate input for motorInfo
        self._check_argument_validity(pwm)

        self._motorInfo: dict = motorInfo
        self._pins = pins

        self._leftBackwardPin: int = self._set_direction_pin("left", "backward")
        self._leftForwardPin: int = self._set_direction_pin("left", "forward")
        self._rightBackwardPin: int = self._set_direction_pin("right", "backward")
        self._rightForwardPin: int = self._set_direction_pin("right", "forward")
        self._enA: int = pins["ENA"]
        self._enB: int = pins["ENB"]

        self._pwmMin = pwm["Minimum"]
        self._pwmMax = pwm["Maximum"]

        self._minSpeed = 0
        self._maxSpeed = 100

        self._pwmA = None
        self._pwmB = None

        self._speedToPwmValues: dict[int: float] = self._getSpeedValuesMappedToPwmValues()

    def _set_direction_pin(self, side: str, direction: str) -> int:
        print(self._motorInfo)
        if self._motorInfo["Sides"]["MotorA"] == side:
            motorPins = [1, 2]
            if self._motorInfo["ReverseDirection"]["MotorA"]:
                if direction == "forward":
                    return motorPins[0]
                if direction == "backward":
                    return motorPins[1]
            else:
                if direction == "forward":
                    return motorPins[1]
                if direction == "backward":
                    return motorPins[0]

        elif self._motorInfo["Sides"]["MotorB"] == side:
            motorPins = [3, 4]
            if self._motorInfo["ReverseDirection"]["MotorB"]:
                if direction == "forward":
                    return motorPins[0]
                if direction == "backward":
                    return motorPins[1]
            else:
                if direction == "forward":
                    return motorPins[1]
                if direction == "backward":
                    return motorPins[0]


    def setup(self, startSpeed):
        GPIO.setup(self._leftBackwardPin, GPIO.OUT)
        GPIO.setup(self._leftForwardPin, GPIO.OUT)
        GPIO.setup(self._rightBackwardPin, GPIO.OUT)
        GPIO.setup(self._rightForwardPin, GPIO.OUT)
        GPIO.setup(self._enA, GPIO.OUT)
        GPIO.setup(self._enB, GPIO.OUT)

        self._pwmA = GPIO.PWM(self._enA, 100)
        self._pwmB = GPIO.PWM(self._enB, 100)

        self._pwmA.start(startSpeed)
        self._pwmB.start(startSpeed)

    @property
    def pins(self) -> list[int]:
        return list(self._pins.values())

    def change_speed(self, speed):
        for pwm in [self._pwmA, self._pwmB]:
            pwm.ChangeDutyCycle(speed)

    def drive(self):
        GPIO.output(self._leftForwardPin, GPIO.HIGH)
        GPIO.output(self._rightForwardPin, GPIO.HIGH)
        GPIO.output(self._leftBackwardPin, GPIO.LOW)
        GPIO.output(self._rightBackwardPin, GPIO.LOW)

    def reverse(self):
        GPIO.output(self._leftForwardPin, GPIO.LOW)
        GPIO.output(self._rightForwardPin, GPIO.LOW)
        GPIO.output(self._leftBackwardPin, GPIO.HIGH)
        GPIO.output(self._rightBackwardPin, GPIO.HIGH)

    def turn_left(self):
        GPIO.output(self._leftForwardPin, GPIO.HIGH)
        GPIO.output(self._rightForwardPin, GPIO.LOW)
        GPIO.output(self._leftBackwardPin, GPIO.LOW)
        GPIO.output(self._rightBackwardPin, GPIO.HIGH)

    def turn_right(self):
        GPIO.output(self._leftForwardPin, GPIO.LOW)
        GPIO.output(self._rightForwardPin, GPIO.HIGH)
        GPIO.output(self._leftBackwardPin, GPIO.HIGH)
        GPIO.output(self._rightBackwardPin, GPIO.LOW)

    def stop(self):
        GPIO.output(self._leftForwardPin, GPIO.LOW)
        GPIO.output(self._rightForwardPin, GPIO.LOW)
        GPIO.output(self._leftBackwardPin, GPIO.LOW)
        GPIO.output(self._rightBackwardPin, GPIO.LOW)

    def cleanup(self) -> None:
        self._pwmA.stop()
        self._pwmB.stop()

    def _getSpeedValuesMappedToPwmValues(self) -> dict[int: float]:
        return {
            speed: map_value_to_new_scale(speed, self._pwmMin, self._pwmMax, self._minSpeed, self._maxSpeed, 1)
            for speed in range(self._minSpeed, self._maxSpeed + 1)}

    def _check_argument_validity(self, pwm: dict[str: int]) -> None:
        # check that the pwm values are within valid range
        check_if_num_is_in_interval(pwm["Minimum"], 0, 100, "MinimumMotorPWM")
        check_if_num_is_in_interval(pwm["Maximum"], 0, 100, "MaximumMotorPWM")
