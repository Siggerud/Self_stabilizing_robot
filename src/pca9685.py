class PCA9685:
    def __init__(self):
        self._kit = None

    def setup(self):
        # this import sets GPIO mode to BCM, so to avoid interfering with other processes, it's
        # better to import it after initialization
        from adafruit_servokit import ServoKit

        self._kit = ServoKit(channels=16)

    def set_servo_to_angle(self, channel: int, angle: int):
        self._kit.servo[channel].angle = angle

