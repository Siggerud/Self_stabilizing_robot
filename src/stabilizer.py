from motionTrackingDevice import MotionTrackingDevice


class Stabilizer:
    def __init__(self,
                 motionTrackingDevice: MotionTrackingDevice,
                 rollTreshold: int,
                 pitchTreshold: int,
                 stabilizerChannels: dict[str, int]
                 ):
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
