import subprocess
from configparser import ConfigParser

output: str = subprocess.check_output("bluetoothctl devices Connected", shell=True).decode("utf-8")
if output == "":
    print("No bluetooth headphones connected")
    exit()

# extract the microphone name
microphoneName: str = output.split()[-1].strip()
print(f"Found bluetooth headphones with name: {microphoneName}")

# set the microphone name in the config file
answer = input("Do you want to set this as the default microphone? (y/n): ")
if answer == "n":
    exit()
elif answer == "y":
    config = ConfigParser()
    config.read("../src/config.ini")
    config["Audio.specs"]["microphone_name"] = microphoneName
    with open("../src/config.ini", "w") as configFile:
        config.write(configFile)
    print(f"Default microphone set to {microphoneName}")

