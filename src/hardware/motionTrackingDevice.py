from math import atan, pi
from time import time, sleep

from mpu6050 import mpu6050

from exceptions import MotionTrackingDeviceException
from utility.roboCarHelper import check_if_num_is_in_interval
from statistics import mean


class MotionTrackingDevice:
    def __init__(self, rollAxis: str, pitchAxis: str, offsets: dict[str: float], stabilizeOnStartup: bool):
        self._check_argument_validity(rollAxis, pitchAxis, offsets)

        self._mpu6050 = mpu6050(0x68)
        self._rollAxis: str = rollAxis
        self._pitchAxis: str = pitchAxis
        self._yawAxis: str = "z"

        self._offsetRoll = offsets[rollAxis]
        self._offsetPitch = offsets[pitchAxis]
        self._stabilizeOnStartup: bool = stabilizeOnStartup

        self._tLoop: float = 0

        self._rollComp: float = 0
        self._pitchComp: float = 0

        self._errorRoll: float = 0
        self._errorPitch: float = 0

        self._confidenceFactor: float = 0.94
        self._errorFactor: float = 0.01

        self._count = 0

    def setup(self) -> None:
        if self._stabilizeOnStartup:
            print("Setting stabilization offset values based on current position")
            self._set_offset_values()
            print("Stabilization offset values set")

    def get_roll_and_pitch(self) -> tuple[float, float]:
        tStart: float = self._set_start_time()

        rollAccel, pitchAccel, yawAccel = self._unpack_accelerometer_data()
        rollAccelAngle, pitchAccelAngle = self._calculate_angles_from_accelerometer_data(rollAccel, pitchAccel,
                                                                                         yawAccel)

        # TODO: rename these variables
        xGyro, yGyro = self._unpack_gyroscope_data()
        rollGyroAngleDelta, pitchGyroAngleDelta = self._calculate_angle_delta_from_gyro_values(xGyro, yGyro)

        self._calculate_complimentary_roll_and_pitch_angles(rollAccelAngle, pitchAccelAngle, rollGyroAngleDelta,
                                                            pitchGyroAngleDelta)
        self._add_error_value_to_complimentary_angles()

        self._calculate_steady_state_error_values(rollAccelAngle, pitchAccelAngle)

        self._set_loop_time(tStart)

        return self._rollComp, self._pitchComp

    def _set_loop_time(self, tStart: float) -> None:
        self._tLoop = time() - tStart

    def _set_start_time(self) -> float:
        return time()

    def _calculate_steady_state_error_values(self, rollAccelAngle: float, pitchAccelAngle: float) -> None:
        self._errorRoll = self._errorRoll + (rollAccelAngle - self._rollComp) * self._tLoop
        self._errorPitch = self._errorPitch + (pitchAccelAngle - self._pitchComp) * self._tLoop

    def _add_error_value_to_complimentary_angles(self) -> None:
        self._rollComp += self._errorRoll * self._errorFactor
        self._pitchComp += self._errorPitch * self._errorFactor

    def _calculate_complimentary_roll_and_pitch_angles(self,
                                                       rollAccelAngle: float,
                                                       pitchAccelAngle: float,
                                                       rollGyroAngleDelta: float,
                                                       pitchGyroAngleDelta: float) -> None:
        # calculate the complimentary angles based on data from both the accelerometer and the gyro data
        self._rollComp = rollAccelAngle * (1 - self._confidenceFactor) + (
                self._rollComp + rollGyroAngleDelta) * self._confidenceFactor
        self._pitchComp = pitchAccelAngle * (1 - self._confidenceFactor) + (
                self._pitchComp + pitchGyroAngleDelta) * self._confidenceFactor

    def _calculate_angle_delta_from_gyro_values(self, xGyro: float, yGyro: float) -> (float, float):
        # Calculate the latest angles deltas based on gyro data
        rollGyroAngleDelta: float = xGyro * self._tLoop
        pitchGyroAngleDelta: float = yGyro * self._tLoop

        return rollGyroAngleDelta, pitchGyroAngleDelta

    def _unpack_gyroscope_data(self) -> (float, float):
        # Read the gyro data
        gyro_data: dict[str: float] = self._mpu6050.get_gyro_data()

        # unpack the gyro data
        xGyro: float = gyro_data[self._pitchAxis]
        yGyro: float = gyro_data[self._rollAxis]

        return xGyro, yGyro

    def _calculate_angles_from_accelerometer_data(self, rollAccel: float, pitchAccel: float, yawAccel: float) -> (float, float):
        # Calculate the latest angles based on accelerometer data and subtract the offsets
        rollAccelAngle = self._calculate_angles_in_degrees(rollAccel, yawAccel) - self._offsetRoll
        pitchAccelAngle = self._calculate_angles_in_degrees(pitchAccel, yawAccel) - self._offsetPitch

        return rollAccelAngle, pitchAccelAngle

    def _unpack_accelerometer_data(self) -> (float, float, float):
        # Read the sensor data
        accelerometer_data: dict[str: float] = self._mpu6050.get_accel_data(g=True)  # get value in gravity units

        # unpack the accelerometer data
        rollAccel = self._set_value_equal_to_1_if_greater(accelerometer_data[self._rollAxis])
        pitchAccel = self._set_value_equal_to_1_if_greater(accelerometer_data[self._pitchAxis])
        yawAccel = self._set_value_equal_to_1_if_greater(accelerometer_data[self._yawAxis])

        return rollAccel, pitchAccel, yawAccel

    # TODO: make a test of this method
    def _set_value_equal_to_1_if_greater(self, accelValue: float) -> float:
        if accelValue > 1:
            return 1
        return accelValue

    def _calculate_angles_in_degrees(self, opposite: float, adjacent: float) -> float:
        return atan(opposite / adjacent) * 180 / pi

    def _check_argument_validity(self, rollAxis: str, pitchAxis: str, offsets: dict[str: float]):
        if {rollAxis, pitchAxis} != {"x", "y"}:
            raise MotionTrackingDeviceException("Inputs for roll- and pitch axis must be x and y")

        for offset in offsets.values():
            check_if_num_is_in_interval(offset, -90, 90, "offset")

    # TODO: consider making this a static method
    def _set_offset_values(self) -> None:
        numOfIterations = 25
        sleepTime = 0.2
        print(f"This takes approximately {int(numOfIterations * sleepTime)} seconds...")
        offsetXReadings: list = []
        offsetYReadings: list = []
        for _ in range(numOfIterations):
            xAccel: float = self._mpu6050.get_accel_data()["x"]
            yAccel: float = self._mpu6050.get_accel_data()["y"]
            zAccel: float = self._mpu6050.get_accel_data()["z"]

            print(xAccel)
            print(yAccel)
            print(zAccel)

            offsetXReadings.append(round(atan(xAccel / zAccel) / 2 / pi * 360, 3))
            offsetYReadings.append(round(atan(yAccel / zAccel) / 2 / pi * 360, 3))

            # sleep to not overload mpu6050 sensor
            sleep(0.1)

        offsets: dict[str: float] = {
            "x": round(mean(offsetXReadings), 3),
            "y": round(mean(offsetYReadings), 3)
        }

        self._offsetRoll = offsets[self._rollAxis]
        self._offsetPitch = offsets[self._pitchAxis]
