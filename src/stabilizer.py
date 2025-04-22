from exceptions import StabilizerException
from src.hardware.motionTrackingDevice import MotionTrackingDevice
from src.hardware.pca9685 import PCA9685
from src.utility.roboCarHelper import get_duplicates_in_list, extend_with_reversed
from robotProcess import RobotProcess


class Stabilizer(RobotProcess):
    def __init__(self,
                 motionTrackingDevice: MotionTrackingDevice,
                 pca9685: PCA9685,
                 rollTreshold: int,
                 pitchTreshold: int,
                 stabilizerChannels: dict[str, int]
                 ):
        self._validate_input(rollTreshold, pitchTreshold, stabilizerChannels)
        #TODO: have tresholds as a dictionary argument
        self._motionTrackingDevice: MotionTrackingDevice = motionTrackingDevice
        self._pca9685 = pca9685
        self._rollTreshold: int = rollTreshold
        self._pitchTreshold: int = pitchTreshold
        self._servoChannels: dict[str: int] = stabilizerChannels
        self._servoAngles: dict[str: int] = {  # keeps track of the current angle of the servos
            "frontLeft": 180,
            "frontRight": 0,
            "rearLeft": 0,
            "rearRight": 180
        }

        self._verticalServoAngles: dict[str: int] = self._servoAngles.copy()

        self._oppositeSidesOfCarRollAndPitch: dict[str: str] = {
            "rearLeft": "frontRight",
            "rearRight": "frontLeft",
        }
        extend_with_reversed(self._oppositeSidesOfCarRollAndPitch)

        self._oppositeSidesOfCarPitch: dict[str: str] = {
            "frontRight": "rearRight",
            "frontLeft": "rearLeft",
        }
        extend_with_reversed(self._oppositeSidesOfCarPitch)

        self._oppositeSidesOfCarRoll: dict[str: str] = {
            "frontRight": "frontLeft",
            "rearRight": "rearLeft",
        }
        extend_with_reversed(self._oppositeSidesOfCarRoll)

    def setup(self):
        self._pca9685.setup()
        self._motionTrackingDevice.setup()

        # set all wheels to vertical position
        self._set_all_legs_vertical()

    @property
    def gpio_pins(self) -> list[int]:
        return [3, 5]

    @property
    def gpio_process(self) -> bool:
        return False

    def stabilize(self):
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        rollDirection, pitchDirection = self._get_roll_and_pitch_direction(rollAngle, pitchAngle)

        self._stabilize_car_from_offset_direction(rollDirection, pitchDirection)

    def cleanup(self) -> None:
        self._set_all_legs_vertical()

    def _get_roll_and_pitch_direction(self, rollAngle: float, pitchAngle: float) -> (str, str):
        rollDirection: str = self._get_roll_direction(rollAngle)
        pitchDirection: str = self._get_pitch_direction(pitchAngle)

        return rollDirection, pitchDirection

    def _stabilize_car_from_offset_direction(self, rollDirection: str, pitchDirection: str) -> None:
        if pitchDirection == "stable" and rollDirection == "stable":
            return # exit method if car is relatively stable
        # always prioritize to get legs vertical over getting legs horizontal
        elif pitchDirection == "forward" and rollDirection == "left":
            self._stabilize_offset_pitch_and_roll(saggingSide="frontLeft")

        elif pitchDirection == "forward" and rollDirection == "right":
            self._stabilize_offset_pitch_and_roll(saggingSide="frontRight")

        elif pitchDirection == "backward" and rollDirection == "left":
            self._stabilize_offset_pitch_and_roll(saggingSide="rearLeft")

        elif pitchDirection == "backward" and rollDirection == "right":
            self._stabilize_offset_pitch_and_roll(saggingSide="rearRight")

        # positive pitch angle is forward tilt
        elif pitchDirection == "forward" and rollDirection == "stable":
            self._stabilize_offset_pitch(saggingSides=("frontRight", "frontLeft"))

        elif pitchDirection == "backward" and rollDirection == "stable":
            self._stabilize_offset_pitch(saggingSides=("rearRight", "rearLeft"))

        # positive roll angle is left tilt
        elif rollDirection == "left" and pitchDirection == "stable":  # tilts left
            self._stabilize_offset_roll(saggingSides=("frontLeft", "rearLeft"))

        elif rollDirection == "right" and pitchDirection == "stable":  # tilts right
            self._stabilize_offset_roll(saggingSides=("frontRight", "rearRight"))

    def _stabilize_offset_roll(self, saggingSides: tuple) -> None:
        if not self._check_if_servo_is_vertical(saggingSides[0]) and not self._check_if_servo_is_vertical(
                saggingSides[1]):
            self._lower_wheel_by_one_degree(saggingSides[0])
            self._lower_wheel_by_one_degree(saggingSides[1])

        # if left legs are fully stretched, then lower right legs, but no longer than horizontal
        elif not self._check_if_servo_is_horizontal(
                self._oppositeSidesOfCarRoll[saggingSides[0]]) and not self._check_if_servo_is_horizontal(
            self._oppositeSidesOfCarRoll[saggingSides[1]]):
            self._raise_wheel_by_one_degree(self._oppositeSidesOfCarRoll[saggingSides[0]])
            self._raise_wheel_by_one_degree(self._oppositeSidesOfCarRoll[saggingSides[1]])

    def _stabilize_offset_pitch(self, saggingSides: tuple) -> None:
        # check if sagging side legs are vertical, if not, then lower them
        if not self._check_if_servo_is_vertical(saggingSides[0]) and not self._check_if_servo_is_vertical(
                saggingSides[1]):
            self._lower_wheel_by_one_degree(saggingSides[0])
            self._lower_wheel_by_one_degree(saggingSides[1])

        # check if legs on opposite side are horizontal, if not, then raise them
        elif not self._check_if_servo_is_horizontal(
                self._oppositeSidesOfCarPitch[saggingSides[0]]) and not self._check_if_servo_is_horizontal(
            self._oppositeSidesOfCarPitch[saggingSides[1]]):
            self._raise_wheel_by_one_degree(self._oppositeSidesOfCarPitch[saggingSides[0]])
            self._raise_wheel_by_one_degree(self._oppositeSidesOfCarPitch[saggingSides[1]])

    def _stabilize_offset_pitch_and_roll(self, saggingSide: str) -> None:
        # check if sagging side has a vertical leg, if not lower it
        if not self._check_if_servo_is_vertical(saggingSide):
            self._lower_wheel_by_one_degree(saggingSide)

        # if sagging side has a vertical leg, then raise the leg on the opposite side
        elif not self._check_if_servo_is_horizontal(self._oppositeSidesOfCarRollAndPitch[saggingSide]):
            self._raise_wheel_by_one_degree(self._oppositeSidesOfCarRollAndPitch[saggingSide])

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
