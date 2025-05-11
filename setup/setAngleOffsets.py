import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mpu6050 import mpu6050
from math import atan, pi
import yaml
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
fullFilePath: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/config/stabilizer.yml')

# Load the YAML file
with open(fullFilePath, "r") as file:
    data = yaml.safe_load(file)  # Load as dictionary

data["Offsets"]["offset_x"] = offsetX
data["Offsets"]["offset_y"] = offsetY

# Save the updated YAML back to the file
with open(fullFilePath, "w") as file:
    yaml.dump(data, file, default_flow_style=False)

print(f"offset_x value set to {offsetX} and offset_y value set to {offsetY}")
