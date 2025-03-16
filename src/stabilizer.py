from motionTrackingDevice import MotionTrackingDevice
from exceptions import StabilizerException
from robotProcess import RobotProcess
from pca9685 import PCA9685

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

        self._count = 0
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
        self._pca9685.set_servo_to_angle(self._servoChannels["frontLeft"], self._servoAngles["frontLeft"])
        self._pca9685.set_servo_to_angle(self._servoChannels["rearLeft"], self._servoAngles["rearLeft"])
        self._pca9685.set_servo_to_angle(self._servoChannels["frontRight"], self._servoAngles["frontRight"])
        self._pca9685.set_servo_to_angle(self._servoChannels["rearRight"], self._servoAngles["rearRight"])

    @property
    def gpio_pins(self) -> list[int]:
        return [3, 5]

    @property
    def gpio_process(self) -> bool:
        return False

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 300 == 0:
            print(f"Roll angle: {rollAngle}, Pitch angle: {pitchAngle}")
            print(f"Max roll: {self._maxRoll}, Max pitch: {self._maxPitch}")
            print()

        # positive pitch angle is forward tilt
        # positive roll angle is left tilt
        if rollAngle > self._rollTreshold: # tilts left
            # first check if left legs are fully stretched, if not then stretch them out
            if not self._check_if_servo_is_vertical("frontLeft") and not self._check_if_servo_is_vertical("rearLeft"):
                self._lower_wheel_by_one_degree("frontLeft")
                self._lower_wheel_by_one_degree("rearLeft")
            print(self._get_current_angle("frontRight"))
            # if left legs are fully stretched, then lower right legs, but no longer than horizontal
            elif self._check_if_servo_is_horizontal("frontRight") and self._check_if_servo_is_horizontal("rearRight"):
                self._raise_wheel_by_one_degree("frontRight")
                self._raise_wheel_by_one_degree("rearRight")
            if self._overRollTreshold == False:
                print("Roll angle is too high")
                self._overRollTreshold = True
        elif rollAngle < -self._rollTreshold: # tilts right
            # first check if right legs are fully stretched
            if not self._check_if_servo_is_vertical("frontRight") and not self._check_if_servo_is_vertical("rearRight"):
                self._lower_wheel_by_one_degree("frontRight")
                self._lower_wheel_by_one_degree("rearRight")

            # if left legs are fully stretched, then lower right legs, but no longer than horizontal
            elif self._get_current_angle("frontLeft") > 90 and self._get_current_angle("rearLeft") < 90:
                self._raise_wheel_by_one_degree("frontLeft")
                self._raise_wheel_by_one_degree("rearLeft")

            if self._overRollTreshold == False:
                print("Roll angle is too low")
                self._overRollTreshold = True
        else:
            if self._overRollTreshold == True:
                print("Roll angle back to ok levels")

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

    def cleanup(self) -> None:
        pass

    def _validate_input(self, rollTreshold: int, pitchTreshold: int, stabilizerChannels: dict[str: int]):
        if len(stabilizerChannels) != len(set(stabilizerChannels.values())):
            #TODO: give the duplicate channels in the message
            raise StabilizerException("Not all servo channels are unique")

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



