from motionTrackingDevice import MotionTrackingDevice
from exceptions import StabilizerException
from robotProcess import RobotProcess
from pca9685 import PCA9685
from roboCarHelper import get_duplicates_in_list

class Stabilizer(RobotProcess):
    def __init__(self,
                 motionTrackingDevice: MotionTrackingDevice,
                 rollTreshold: int,
                 pitchTreshold: int,
                 stabilizerChannels: dict[str, int]
                 ):
        self._validate_input(rollTreshold, pitchTreshold, stabilizerChannels)

        self._motionTrackingDevice: MotionTrackingDevice = motionTrackingDevice
        self._rollTreshold: int = rollTreshold
        self._pitchTreshold: int = pitchTreshold
        self._servoChannels: dict[str: int] = stabilizerChannels
        self._servoAngles: dict[str: int] = { # keeps track of the current angle of the servos
            "frontLeft": 180,
            "frontRight": 0,
            "rearLeft": 0,
            "rearRight": 180
        }

        self._verticalServoAngles: dict[str: int] = self._servoAngles.copy()

        self._pca9685 = PCA9685()

        #self._count = 0
        self._lastFrontLeftAngle = 90
        self._lastRearLeftAngle = 90
        self._kit = None
        self._overRollTreshold = False
        self._overPitchTreshold = False
        self._maxRoll = 0
        self._maxPitch = 0

    def setup(self):
        self._pca9685.setup()

        # set all wheels to vertical position
        self._set_all_legs_vertical()

    @property
    def gpio_pins(self) -> list[int]:
        return [3, 5]

    @property
    def gpio_process(self) -> bool:
        return False

    def stabilize(self):
        # self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        # if self._count % 300 == 0:
        #     print(f"Roll angle: {rollAngle}, Pitch angle: {pitchAngle}")
        #     print(f"Max roll: {self._maxRoll}, Max pitch: {self._maxPitch}")
        #     print()

        #TODO: stabilize on startup, or at least give the option to do so

        rollDirection: str = self._get_roll_direction(rollAngle)
        pitchDirection:str = self._get_pitch_direction(pitchAngle)

        # always prioritize to get legs vertical over getting legs horizontal
        if pitchDirection == "forward" and rollDirection == "left":
            if not self._check_if_servo_is_vertical("frontLeft"):
                self._lower_wheel_by_one_degree("frontLeft")

            elif not self._check_if_servo_is_horizontal("rearRight"):
                self._raise_wheel_by_one_degree("rearRight")

        elif pitchDirection == "forward" and rollDirection == "right":
            if not self._check_if_servo_is_vertical("frontRight"):
                self._lower_wheel_by_one_degree("frontRight")

            elif not self._check_if_servo_is_horizontal("rearLeft"):
                self._raise_wheel_by_one_degree("rearLeft")

        elif pitchDirection == "backward" and rollDirection == "left":
            if not self._check_if_servo_is_vertical("rearLeft"):
                self._lower_wheel_by_one_degree("rearLeft")

            elif not self._check_if_servo_is_horizontal("frontRight"):
                self._raise_wheel_by_one_degree("frontRight")

        elif pitchDirection == "backward" and rollDirection == "right":
            if not self._check_if_servo_is_vertical("rearRight"):
                self._lower_wheel_by_one_degree("rearRight")

            elif not self._check_if_servo_is_horizontal("frontLeft"):
                self._raise_wheel_by_one_degree("frontLeft")

        # positive pitch angle is forward tilt
        if pitchDirection == "forward" and rollDirection == "stable":
            # check if front legs are vertical, if not, then lower them
            if not self._check_if_servo_is_vertical("frontRight") and not self._check_if_servo_is_vertical("frontLeft"):
                self._lower_wheel_by_one_degree("frontRight")
                self._lower_wheel_by_one_degree("frontLeft")

            # check of rear legs are horizontal, if not, then raise them
            elif not self._check_if_servo_is_horizontal("rearRight") and not self._check_if_servo_is_horizontal("rearLeft"):
                self._raise_wheel_by_one_degree("rearRight")
                self._raise_wheel_by_one_degree("rearLeft")

        elif pitchDirection == "backward" and rollDirection == "stable":
            if not self._check_if_servo_is_vertical("rearRight") and not self._check_if_servo_is_vertical("rearLeft"):
                self._lower_wheel_by_one_degree("rearRight")
                self._lower_wheel_by_one_degree("rearLeft")

            elif not self._check_if_servo_is_horizontal("frontRight") and not self._check_if_servo_is_horizontal("frontLeft"):
                self._raise_wheel_by_one_degree("frontRight")
                self._raise_wheel_by_one_degree("frontLeft")

        # positive roll angle is left tilt
        if rollDirection == "left" and pitchDirection == "stable": # tilts left
            # first check if left legs are fully stretched, if not then stretch them out
            if not self._check_if_servo_is_vertical("frontLeft") and not self._check_if_servo_is_vertical("rearLeft"):
                self._lower_wheel_by_one_degree("frontLeft")
                self._lower_wheel_by_one_degree("rearLeft")

            # if left legs are fully stretched, then lower right legs, but no longer than horizontal
            elif not self._check_if_servo_is_horizontal("frontRight") and not self._check_if_servo_is_horizontal("rearRight"):
                self._raise_wheel_by_one_degree("frontRight")
                self._raise_wheel_by_one_degree("rearRight")
            if self._overRollTreshold == False:
                print("Roll angle is too high")
                self._overRollTreshold = True
        elif rollDirection == "right" and pitchDirection == "stable": # tilts right
            # first check if right legs are fully stretched
            if not self._check_if_servo_is_vertical("frontRight") and not self._check_if_servo_is_vertical("rearRight"):
                self._lower_wheel_by_one_degree("frontRight")
                self._lower_wheel_by_one_degree("rearRight")

            # if left legs are fully stretched, then lower right legs, but no longer than horizontal
            elif not self._check_if_servo_is_horizontal("frontLeft") and not self._check_if_servo_is_horizontal("rearLeft"):
                self._raise_wheel_by_one_degree("frontLeft")
                self._raise_wheel_by_one_degree("rearLeft")

    def cleanup(self) -> None:
        self._set_all_legs_vertical()

    def _get_pitch_direction(self, pitchAngle: float) -> str:
        if pitchAngle > self._pitchTreshold:
            return "forward"
        elif pitchAngle < -self._pitchTreshold:
            return "backward"
        return "stable"

    def _get_roll_direction(self, rollAngle: float) -> str:
        if rollAngle > self._rollTreshold:
            return "left"
        elif rollAngle < -self._rollTreshold:
            return "right"
        return "stable"

    def _raise_wheel_by_one_degree(self, servo: str):
        if servo == "rearRight" or servo == "frontLeft":
            increment = -1
        elif servo == "rearLeft" or servo == "frontRight":
            increment = 1

        currentAngle: int = self._get_current_angle(servo)
        self._move_wheel(servo, currentAngle + increment)

    def _lower_wheel_by_one_degree(self, servo: str):
        if servo == "rearLeft" or servo == "frontRight":
            increment = -1
        elif servo == "frontLeft" or servo == "rearRight":
            increment = 1

        currentAngle: int = self._get_current_angle(servo)
        self._move_wheel(servo, currentAngle + increment)

    def _move_wheel(self, servo: str, angle: int):
        self._pca9685.set_servo_to_angle(self._servoChannels[servo], angle)
        self._set_current_angle(servo, angle)

    def _set_current_angle(self, servo: str, angle: int):
        if 180 >= angle >= 0:
            self._servoAngles[servo] = angle

    def _get_current_angle(self, servo: str) -> int:
        return self._servoAngles[servo]

    def _check_if_servo_is_vertical(self, servo: str) -> bool:
        if self._get_current_angle(servo) == self._verticalServoAngles[servo]:
            return True
        return False

    def _check_if_servo_is_horizontal(self, servo: str) -> bool:
        if self._get_current_angle(servo) == 90:
            return True
        return False

    def _set_all_legs_vertical(self) -> None:
        self._pca9685.set_servo_to_angle(self._servoChannels["frontLeft"], self._verticalServoAngles["frontLeft"])
        self._pca9685.set_servo_to_angle(self._servoChannels["rearLeft"], self._verticalServoAngles["rearLeft"])
        self._pca9685.set_servo_to_angle(self._servoChannels["frontRight"], self._verticalServoAngles["frontRight"])
        self._pca9685.set_servo_to_angle(self._servoChannels["rearRight"], self._verticalServoAngles["rearRight"])

    def _validate_input(self, rollTreshold: int, pitchTreshold: int, stabilizerChannels: dict[str: int]):
        if len(stabilizerChannels) != len(set(stabilizerChannels.values())):
            duplicates: list[int] = get_duplicates_in_list(stabilizerChannels)
            raise StabilizerException(f"Servo channels ({duplicates}) are not unique!")

        if min(stabilizerChannels.values()) < 0 or max(stabilizerChannels.values()) > 15:
            raise StabilizerException("Servo channels must be in range from 0 to 15")

        if self._check_if_treshold_out_of_bounds(rollTreshold):
            raise StabilizerException(f"Treshold for roll is out of bounds, set between 0 and 90 degrees")

        if self._check_if_treshold_out_of_bounds(pitchTreshold):
            raise StabilizerException(f"Treshold for pitch is out of bounds, set between 0 and 90 degrees")

    def _check_if_treshold_out_of_bounds(self, treshold: int) -> bool:
        if treshold < 0 or treshold > 90:
            return True
        return False



