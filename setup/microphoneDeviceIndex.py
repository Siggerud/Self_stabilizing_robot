import speech_recognition as sr
import sounddevice

for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Microphone with index {index}: {name}")
