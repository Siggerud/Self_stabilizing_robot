from motionTrackingDevice import MotionTrackingDevice
from exceptions import StabilizerException
from robotProcess import RobotProcess
from pca9685 import PCA9685
from time import sleep

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

        self._pca9685 = PCA9685()

        self._count = 0
        self._lastFrontLeftAngle = 90
        self._kit = None
        self._overRollTreshold = False
        self._overPitchTreshold = False
        self._maxRoll = 0
        self._maxPitch = 0

    def setup(self):
        self._pca9685.setup()
        self._pca9685.print_actuation_range(self._stabilizerChannels["frontLeft"])
        self._pca9685.print_actuation_range(self._stabilizerChannels["rearLeft"])

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
            if (self._pca9685.get_servo_angle(self._stabilizerChannels["frontRight"]) + 1) > 180 and (self._pca9685.get_servo_angle(self._stabilizerChannels["rearRight"]) -1) < 0:
                frontLeftNewAngle = self._lastFrontLeftAngle + 1
                self._lastFrontLeftAngle += 1
                rearLeftNewAngle = int(self._pca9685.get_servo_angle(self._stabilizerChannels["rearLeft"]) - 1)
                print("front left: " + str(frontLeftNewAngle))
                print("rear left: " + str(rearLeftNewAngle))
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontLeft"], frontLeftNewAngle)
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearLeft"], rearLeftNewAngle)
                #print("front left: " + str(int(self._pca9685.get_servo_angle(self._stabilizerChannels["frontLeft"]))))
                #print("rear left: " + str(int(self._pca9685.get_servo_angle(self._stabilizerChannels["rearLeft"]))))
            else:
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontRight"], self._pca9685.get_servo_angle(self._stabilizerChannels["frontRight"]) +1)
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearRight"], self._pca9685.get_servo_angle(self._stabilizerChannels["rearRight"]) -1)
            if self._overRollTreshold == False:
                print("Roll angle is too high")
                self._overRollTreshold = True
        elif rollAngle < -self._rollTreshold: # tilts right
            if self._overRollTreshold == False:
                print("Roll angle is too low")
                #TODO: these are set to move correctly now, build on that
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontLeft"], 45)
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearLeft"], 135)
                self._overRollTreshold = True
        else:
            if self._overRollTreshold == True:
                print("Roll angle back to ok levels")
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontLeft"], 90)
                self._lastFrontLeftAngle = 90
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontRight"], 90)
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearLeft"], 90)
                self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearRight"], 90)
                self._overRollTreshold = False

        # if pitchAngle > self._pitchTreshold:
        #     if self._overPitchTreshold == False:
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontRight"], 45)
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontLeft"], 45)
        #         print("Pitch angle is too high")
        #         self._overPitchTreshold = True
        # elif pitchAngle < -self._pitchTreshold:
        #     if self._overPitchTreshold == False:
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearRight"], 45)
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearLeft"], 45)
        #         print("Pitch angle is too high")
        #         self._overPitchTreshold = True
        # else:
        #     if self._overPitchTreshold == True:
        #         print("Pitch angle back to ok levels")
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontLeft"], 90)
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["frontRight"], 90)
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearLeft"], 90)
        #         self._pca9685.set_servo_to_angle(self._stabilizerChannels["rearRight"], 90)
        #         self._overPitchTreshold = False

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



