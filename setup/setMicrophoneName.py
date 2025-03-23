import subprocess
import yaml
from os import path

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
    fullFilePath: str = path.join(path.dirname(path.dirname(__file__)), 'src/config/stabilizer.yml')

    # Load the YAML file
    with open(fullFilePath, "r") as file:
        data = yaml.safe_load(file)  # Load as dictionary

    data["Audio"]["microphone_name"] = microphoneName

    # Save the updated YAML back to the file
    with open(fullFilePath, "w") as file:
        yaml.dump(data, file, default_flow_style=False)
    print(f"Default microphone set to {microphoneName}")

