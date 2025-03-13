class PCA9685:
    def __init__(self):
        self._kit = None

    def setup(self):
        # this import sets GPIO mode to BCM, so to avoid interfering with other processes, it's
        # better to import it after initialization
        from adafruit_servokit import ServoKit

        self._kit = ServoKit(channels=16)

    def print_actuation_range(self, channel):
        print(self._kit.servo[channel].actuation_range)

    def set_servo_to_angle(self, channel: int, angle: int):
        if angle >= 0 and angle <= 180:
            self._kit.servo[channel].angle = angle

    def get_servo_angle(self, channel: int):
        return self._kit.servo[channel].angle