from mpu6050 import mpu6050
from math import atan, pi
from configparser import ConfigParser
from time import sleep

mpu = mpu6050(0x68)

print("Place the car on a horizontal surface...")
answer: str = input("Press y when car is on horizontal surface, and q to quit\n")
if answer == "q":
    print("Quitting setup of offset angles")
    exit()
#TODO: add validition checks of answers
print("\nGetting offset angles...")
numOfIterations = 100
sleepTime = 0.1
print(f"This takes approximately {int(numOfIterations * sleepTime)} seconds...")
offsetXReadings: list = []
offsetYReadings: list = []
for _ in range(numOfIterations):
    xAccel: float = mpu.get_accel_data()["x"]
    yAccel: float = mpu.get_accel_data()["y"]
    zAccel: float = mpu.get_accel_data()["z"]

    offsetXReadings.append(round(atan(xAccel / zAccel) / 2 / pi * 360, 3))
    offsetYReadings.append(round(atan(yAccel / zAccel) / 2 / pi * 360, 3))

    # sleep to not overload mpu6050 sensor
    sleep(0.1)

offsetX: float = round(sum(offsetXReadings) / numOfIterations, 3)
offsetY: float = round(sum(offsetYReadings) / numOfIterations, 3)

print(f"Found offsets: x-axis {offsetX}°, y-axis {offsetY}°")
answer: str = input("Do you want to write these values to the config file? (y/n)\n")
if answer == "n":
    print("Quitting setup of offset angles")
    exit()

print("\nWriting offsets to config file...")
config = ConfigParser()
config.read("../src/config.ini")
config["Stabilizer"]["offset_x"] = str(offsetX)
config["Stabilizer"]["offset_y"] = str(offsetY)
with open("../src/config.ini", "w") as configFile:
    config.write(configFile)
print(f"offset_x value set to {offsetX} and offset_y value set to {offsetY}")
