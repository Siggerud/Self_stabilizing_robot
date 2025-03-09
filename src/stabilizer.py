from motionTrackingDevice import MotionTrackingDevice
from exceptions import StabilizerException
from src.robotProcess import RobotProcess

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
        self._stabilizerChannels: dict[str: int] = stabilizerChannels

        self._count = 0
        self._kit = None
        self._overRollTreshold = False
        self._overPitchTreshold = False
        self._maxRoll = 0
        self._maxPitch = 0

    def setup(self):
        # this import sets GPIO mode to BCM, so to avoid interfering with other processes, it's
        # better to import it after initialization

        #TODO: make a seperate pca9685 class
        from adafruit_servokit import ServoKit

        self._kit = ServoKit(channels=16)

    @property
    def gpio_pins(self) -> list[int]:
        return [3, 5]

    def stabilize(self):
        self._count += 1
        rollAngle, pitchAngle = self._motionTrackingDevice.get_roll_and_pitch()
        if self._count % 300 == 0:
            print(f"Roll angle: {rollAngle}, Pitch angle: {pitchAngle}")
            print(f"Max roll: {self._maxRoll}, Max pitch: {self._maxPitch}")
            print()

        # positive pitch angle is forward tilt
        # positive roll angle is left tilt
        if rollAngle > self._rollTreshold:
            if self._overRollTreshold == False:
                print("Roll angle is too high")
                self._kit.servo[self._stabilizerChannels["frontRight"]].angle = 45
                self._kit.servo[self._stabilizerChannels["rearRight"]].angle = 45
                self._overRollTreshold = True
        elif rollAngle < -self._rollTreshold:
            if self._overRollTreshold == False:
                print("Roll angle is too low")
                self._kit.servo[self._stabilizerChannels["frontLeft"]].angle = 45
                self._kit.servo[self._stabilizerChannels["rearLeft"]].angle = 45
                self._overRollTreshold = True
        else:
            if self._overRollTreshold == True:
                print("Roll angle back to ok levels")
                self._kit.servo[self._stabilizerChannels["frontLeft"]].angle = 90
                self._kit.servo[self._stabilizerChannels["frontRight"]].angle = 90
                self._kit.servo[self._stabilizerChannels["rearLeft"]].angle = 90
                self._kit.servo[self._stabilizerChannels["rearRight"]].angle = 90
                self._overRollTreshold = False

        if pitchAngle > self._pitchTreshold:
            if self._overPitchTreshold == False:
                self._kit.servo[self._stabilizerChannels["frontRight"]].angle = 45
                self._kit.servo[self._stabilizerChannels["frontLeft"]].angle = 45
                print("Pitch angle is too high")
                self._overPitchTreshold = True
        elif pitchAngle < -self._pitchTreshold:
            if self._overPitchTreshold == False:
                self._kit.servo[self._stabilizerChannels["rearRight"]].angle = 45
                self._kit.servo[self._stabilizerChannels["rearLeft"]].angle = 45
                print("Pitch angle is too high")
                self._overPitchTreshold = True
        else:
            if self._overPitchTreshold == True:
                print("Pitch angle back to ok levels")
                self._kit.servo[self._stabilizerChannels["frontLeft"]].angle = 90
                self._kit.servo[self._stabilizerChannels["frontRight"]].angle = 90
                self._kit.servo[self._stabilizerChannels["rearLeft"]].angle = 90
                self._kit.servo[self._stabilizerChannels["rearRight"]].angle = 90
                self._overPitchTreshold = False

    def cleanup(self) -> None:
        pass

    def _validate_input(self, rollTreshold: int, pitchTreshold: int, stabilizerChannels: dict[str: int]):
        if len(stabilizerChannels) != len(set(stabilizerChannels.values())):
            #TODO: give the duplicate channels in the message
            raise StabilizerException("Not all channels are unique")

        if min(stabilizerChannels.values()) < 0 or max(stabilizerChannels.values()) > 15:
            raise StabilizerException("Servo channels must be in range from 0 to 15")

        if self._check_if_treshold_out_of_bounds(rollTreshold):
            raise StabilizerException(f"Treshold for roll is out of bounds, set between 0 and 90 degrees")

        if self._check_if_treshold_out_of_bounds(pitchTreshold):
            raise StabilizerException(f"Treshold for pitch is out of bounds, set between 0 and 90 degrees")

    def _check_if_treshold_out_of_bounds(self, treshold: int) -> bool:
        if treshold < 0 or treshold > 90:
            return True



