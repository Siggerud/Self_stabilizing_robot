# Robocar
![Alt text](Images/robocar.jpg)
The robocar

<br />
<br />
![Alt text](Images/camFeedScreenshot.png)
<br />
Camera feed screenshot from camera onboard robocar

This a robotcar that is operated by voice commands. In addition to the controlling
of the car you can also control the direction of a mounted camera, zooming and
a honking device. To tell wether you've given a valid voice command, signal lights
will give you feedback.

## Prerequisites

### Setup Pi OS
Dowload and install the bookworm 64 bit version to run this project

### Setting up remote connection
1. Enable your VNC connection by first opening the configuration settings
```
sudo raspi-config
```
Enable Interface options -> VNC Enable

2. Find your ip adress for your raspberry pi
```
ifconfig
```
Look under wlan0 and find the adress after inet.

3. Download and install [RealVnc](https://www.realvnc.com/en/connect/download/combined/) for your OS.
Use the ip adress you found earlier to connect to your raspberry pi. Your pi needs to
be on the same network as the station you are connecting to it remotely from.

### Enable ssh
To run the pi from your PC you need to enable ssh
```
sudo systemctl start ssh
```
```
sudo systemctl enable ssh
```

### Clone this repo
Navigate to where you want this repo to be located
```
git clone https://github.com/Siggerud/RoboCar_3.0.git
```

### Downloading necessary libraries
Due to some versions of libraries that might not work
correctly together when installed through pip, we need to use
sudo apt for some of the libraries instead 

First reset pip
```
pip install pip==22.3.1 --break-system-packages
```

Install picamera2
```
pip install picamera2==0.3.22
```

Install opencv-python
```
pip install opencv-python==4.10.0.84
```

Install pytest (Optional, only if you want to run tests)
```
pip install pytest==8.3.4
```

### Setting up pigpio
We need pigpio to control our servo, otherwise
there will be a lot of jitter.
```
sudo apt-get install pigpio=1.79-1+rpt1
```

Setup pipgio service to run at boot
```
sudo systemctl enable pigpiod
```

Then reboot or start pipgio
```
sudo systemctl start pigpiod
```

### Set up speech recognition
#### Connect your headphones/microphones to bluetooth

Start bluetooth and scan for headphones/microphones
```
sudo systemctl start bluetooth
```
```
bluetoothctl
```
```
scan on
```

Copy the number before the name of your microphone

Pair microphone
```
pair XX:XX:XX:XX:XX:XX
```

connect microphone
```
connect XX:XX:XX:XX:XX:XX
```

Trust microphone
```
trust XX:XX:XX:XX:XX:XX
```

#### Add microphone name to config file Alternative 1
If you only have one microphone connected to your pi, you can add the name of the microphone
by a script. However as this is not tested on any other pi than my own, you
will be asked to confirm the name of the microphone before writing it to the config file.<br />

Run the script below
```
python setup/setMicrophoneName.py
```

#### Add microphone name to config file Alternative 2
Get the name of your microphone
```
devices
```

You should see it in this format
```
Device XX:XX:XX:XX:XX:XX NameOfMicrophone
```

Copy the name of your microphone and paste it in the config file under Audio specs
```
[Audio.specs]
language = English (United States)
microphone_name = NameOfMicrophone
```


Exit bluetooth
```
Exit
```

Install utilites for using headphones with Pi
```
sudo apt install bluetooth=5.66-1+rpt1+deb12u2
```
```
sudo apt install bluez=5.66-1+rpt1+deb12u2
```
```
sudo apt install bluez-tools=2.0~20170911.0.7cb788c-4
```
```
sudo apt install rfkill=2.38.1-5+deb12u2
```
```
sudo apt install pulseaudio=16.1+dfsg1-2+rpt1
```
```
sudo apt install pavucontrol=5.0-2
```
Open PulseAudio Volume Control and mark your headphones as default
for input and output device. In the configuration tab set the profile for your
headphones to be HSF/HFP, this is to gain access to the build in microphone in the headphones.

#### Set up microphone for Speech Recognition

Install SpeechRecognition library
```
pip install SpeechRecognition==3.11
```

If you get an error here, then check if you forgot to downgrade pip to 22.3.1

Install SpeechRecognition dependencies
```
sudo apt install portaudio19-dev=19.6.0-1.2
```
```
sudo apt install python3-pyaudio=0.2.13-1+b1
```
```
pip install pyaudio==0.2.13
```
```
sudo apt install flac=1.4.2+ds-2
```

Install sounddevice to avoid massive debug logging
```
pip install sounddevice==0.5.1
```

Run setup/microphoneDeviceIndex to find the index of your microphone. It should
be labelled "pulse"
```
python setup/microphoneDeviceIndex.py
```

Run the script below to test your microphone. Insert the device index you found
in the previous step when prompted. <br />
The script will record your voice and save it to a file. After
the recording it will play the recording back to you, and then delete the file.
```
python setup/microphoneRecordingSetup.py
```

If the step above went as expected, try the speech recognition.<br />
Add the device index again when prompted. Say a few words when the program
tells you to talk. The program will then output what it heard. Ideally it should
be what you said, or something very similar.
```
python setup/speechRecognitionSetup.py
```

If the output is what you communicated, the speech recognition works.

### Setup mpu6050 (gyro and accerelometer) and servos
#### Enable I2C
```
sudo raspi-config
```

Go to Interface options -> I2C -> Enable

#### Install mpu6050 library for raspberry pi
```
pip install mpu6050-raspberrypi==1.2
```

#### Set roll- and pitch axis in config file
Look at the MPU6050. If the x is pointing to the front or back of the car,
you set the x as pitch axis and y as roll axis. If the x points to the
side of the car, you just switch the values.

#### Reset roll- and pitch angles (Optional)
Your MPU6050 sensor might not be completely parallel to the horizontal plane,
and it could be hard to get it exactly right. This might make the servos
try to adjust the car too soon or too late, so you can specify an offset in the config
file. The easiest way to this is by running the command below.
```
python setAngleOffsets.py
```

#### Install servo library
```
pip install adafruit-circuitpython-servokit==1.3.19
```

### Add changes to config file if necessary
All components are setup through a config file that can be modified by you.
You can specify which pins you are using, angle rotation range for the camera
and you can specify the voice commands for specific operations in the language
of your choice.

## Starting up the program
1. Power your xbox controller and wait for it to connect to the pi
2. Connect to your pi via RealVNC
3. Open this project in a terminal 
4. Run the command 
```
python src/run.py
```

## Driving and controlling the car
Give the commands given in the startup message when running the program.

### Exiting the program
Give the exit command given in the start up message to return to stand by mode. To exit completely, press Ctrl + C.

## Appendix

### Wiring
All board pins are given in the <u>board</u> layout, not the BCM layout.
#### Raspberry Pi to L289
GPIO 22 -> IN2 <br />
GPIO 18 -> IN1 <br />
GPIO 16 -> IN4 <br />
GPIO 15 -> IN3 <br />
GPIO 11 -> ENA <br />
GPIO 13 -> ENB <br /> 
GND -> GND

#### L289 to motors
L289 right and left should be based on looking at the
l289 from above reading the text. <br /> 

L289 MOTORA Left -> Right motor front + <br /> 
L289 MOTORA Left -> Right motor back + <br /> 
L289 MOTORA Right -> Right motor back - <br /> 
L289 MOTORA Right -> Right motor front - <br /> 

L289 MOTORB Right -> Left motor front + <br /> 
L289 MOTORB Right -> Left motor back + <br /> 
L289 MOTORB Left -> Left motor back - <br /> 
L289 MOTORB Left -> Left motor front - <br />

#### L289 to batterypack
L289 VMS -> Batterypack +-<br />
L289 GND -> Batterypack -

#### MPU6050 to Raspberry pi
TODO: check if this can be switched to 3.3V
VCC -> 5V <br />
GND -> GND <br />
SDA -> GPIO 3 (SDA) <br />
SCL -> GPIO 5 (SCL) <br />

### PCA9685 to Raspberry pi
VCC -> 5V <br />
GND -> GND <br />
SDA -> GPIO 3 (SDA) <br />
SCL -> GPIO 5 (SCL) <br />

#### PCA9685 channels to servos
Channel 0 -> Front right <br />
Channel 1 -> Rear left <br />
Channel 2 -> Front left <br />
Channel 3 -> Rear right <br />

#### Raspberry pi to horizontal servo
GPIO 37 -> SignalWire <br />
3.3V -> + <br />
GND -> -

#### Raspberry pi to vertical servo
GPIO 33 -> SignalWire <br />
3.3V -> + <br />
GND -> -

#### Raspberry pi to camera
Cameraslot -> Camera

#### Raspberry pi to passive buzzer
GPIO 36 -> +<br />
GND -> -

#### Raspberry pi to LEDs
Green LED<br />
GPIO 32 -> +<br />
GND -> 330 Ohm -> -<br />
<br />
Yellow LED<br />
GPIO 31 -> +<br />
GND -> 330 Ohm -> -<br />
Red LED<br />
GPIO 29 -> +<br />
GND -> 330 Ohm -> -<br />



### Parts list

#### Car handling
Battery pack holding 6AA batteries <br />
4 TT motors <br />
L289N motor driver <br />
4 wheels that attach to motors <br />

#### Other electrical components
Raspberry Pi 4 model B <br />
Raspberry pi Camera Module V2 <br />
Battery pack holding 6AA batteries <br />
Powerbank 10000mah <br />
2 SG90 servos <br />
MPU6050<br />
Passive buzzer <br />
Breadboard <br />
1 green LED light<br />
1 yellow LED light <br />
1 red LED light<br />
3 330 Ohm resistor<br />

#### Structural components
3D printed parts <br />
4x M3 40 mm spacers <br />
4 metal brackets for motors <br />
M3 screws
M3 nuts
female to female wires
male to female wires










