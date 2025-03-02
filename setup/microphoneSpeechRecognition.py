import speech_recognition as sr
import sounddevice
from time import sleep

deviceIndex: int = int(input("Enter the device index: "))
sleepTime: int = 3

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()
r.dynamic_energy_threshold = True
r.energy_threshold = 400  # Experiment with values between 300 and 1500

# Reading Microphone as source
# listening the speech and store in audio_text variable
with sr.Microphone(device_index=deviceIndex) as source:
    print(f"Get ready to talk in {sleepTime} seconds...")
    sleep(sleepTime)
    print("Talk")
    audio_text = r.listen(source)
    print("Time over, thanks")
    # recoginze_() method will throw a request
    # error if the API is unreachable,
    # hence using exception handling

    try:
        # using google speech recognition
        print("Text: " + r.recognize_google(audio_text))
    except sr.UnknownValueError:
        print("Sorry, I did not get that")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition; {e}")