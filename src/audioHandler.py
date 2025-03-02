import speech_recognition as sr
import sounddevice  # to avoid lots of ALSA error
import subprocess
from time import sleep
from exceptions import MicrophoneException

class AudioHandler:

    def __init__(self, exitCommand: str, language: str, microphoneName: str):
        self._check_if_headphones_connected(microphoneName)

        self._deviceIndex: int = self._get_device_index()
        self._exitCommand: str = exitCommand
        self._headPhoneName: str = microphoneName
        self._languageCode: str = self._get_language_code(language)
        self._recognizer = sr.Recognizer()
        self._queue = None

    def setup(self, queue) -> None:
        self._queue = queue

    def set_audio_command(self, flag) -> None:
        spokenWords: str = ""

        # Reading Microphone as source
        # listening the speech and store in audio_text variable
        with sr.Microphone(device_index=self._deviceIndex) as source:
            while not flag.value:
                # adjust to ambient noise on each go
                self._recognizer.adjust_for_ambient_noise(source)
                print("Talk")
                while True:
                    audio_text: str = self._recognizer.listen(source, timeout=None, phrase_time_limit=3)
                    try:
                        # using google speech recognition
                        spokenWords = self._recognizer.recognize_google(audio_text, language=self._languageCode)
                        break
                    except sr.UnknownValueError:
                        # if nothing intelligible is picked up, then try again
                        continue
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition; {e}")
                        break

                spokenWords = self._clean_up_spoken_words(spokenWords)

                # set the command in IPC
                self._queue.put(spokenWords)

                # set flag value to true if command is exit command and break out of loop
                if spokenWords == self._exitCommand:
                    flag.value = True
                    break

                # give some time for the user to observe the effects of the command given before
                # getting ready for the next command
                sleep(0.3)

    def _clean_up_spoken_words(self, spokenWords: str) -> str:
        if "°" in spokenWords:  # change out degree symbol
            # sometimes the ° sign is right next to the number of degrees, so we need to add some space around it
            splitWords: list = spokenWords.split("°")
            strippedWords: list = [word.strip() for word in splitWords]
            rejoinedWords: str = " ° ".join(strippedWords)

            spokenWords = rejoinedWords.replace("°", "degrees")

        print("Command: " + spokenWords)

        return spokenWords.lower().strip()

    def _check_if_headphones_connected(self, headPhoneName: str) -> None:
        sleepTime: int = 10
        numOfTries: int = 0
        treshold: int = 5
        try:
            while numOfTries < treshold:
                output: str = subprocess.check_output("bluetoothctl devices Connected", shell=True).decode("utf-8")

                numOfTries += 1
                if headPhoneName not in output:
                    print(f"Headphone {headPhoneName} not connected. Trying again in {sleepTime} seconds...\n"
                          f"Number of retries: {treshold - numOfTries}\n")
                    sleep(sleepTime)
                else:
                    print(f"Headphone {headPhoneName} connected\n")
                    return
        except KeyboardInterrupt:
            raise MicrophoneException(f"User aborted connecting microphone")

        raise MicrophoneException(f"Headphone {headPhoneName} not connected via bluetooth")

    def _get_device_index(self) -> int:
        connectedMicrophones: list = sr.Microphone.list_microphone_names()
        for index, microphone in enumerate(connectedMicrophones):
            if microphone == "pulse":
                return index

        raise MicrophoneException("No 'pulse' microphone found. Follow readme for proper microphone setup")

    def _get_language_code(self, language) -> str:
        languagesToLanguageCodes: dict = {
            "Afrikaans": "af-ZA",
            "Arabic": "ar-SA",
            "Bulgarian": "bg-BG",
            "Catalan": "ca-ES",
            "Czech": "cs-CZ",
            "Danish": "da-DK",
            "German": "de-DE",
            "Greek": "el-GR",
            "English (Australia)": "en-AU",
            "English (Canada)": "en-CA",
            "English (India)": "en-IN",
            "English (New Zealand)": "en-NZ",
            "English (South Africa)": "en-ZA",
            "English (United Kingdom)": "en-GB",
            "English (United States)": "en-US",
            "Norwegian Bokmål(Norway)": "no-NO",
            "Spanish (Argentina)": "es-AR",
            "Spanish (Bolivia)": "es-BO",
            "Spanish (Chile)": "es-CL",
            "Spanish (Colombia)": "es-CO",
            "Spanish (Costa Rica)": "es-CR",
            "Spanish (Ecuador)": "es-EC",
            "Spanish (El Salvador)": "es-SV",
            "Spanish (Spain)": "es-ES",
            "Spanish (United States)": "es-US",
            "Spanish (Guatemala)": "es-GT",
            "Spanish (Honduras)": "es-HN",
            "Spanish (Mexico)": "es-MX",
            "Spanish (Nicaragua)": "es-NI",
            "Spanish (Panama)": "es-PA",
            "Spanish (Paraguay)": "es-PY"
        }

        try:
            return languagesToLanguageCodes[language]
        except KeyError:
            print(f"Language {language} not found, defaulting to English (United States)")
            return "en-US"



