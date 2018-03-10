# libraries
import requests
import json
import pyaudio
import RPi.GPIO as GPIO

# interface
from interface.lights import Lights

# recording
from record import Record

# ordering
from ordering.speech_processing import SpeechProcessing
import ordering.speech_processing_threads as SpeechProcessingThreads


def main():
    BUTTON = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    button = False

    lights = Lights(3)

    recording_thread = Record(pyaudio.PyAudio())

    url = "http://138.68.71.39:3000/orderkeywords"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
    }
    menu_keywords = requests.request("GET", url, headers=headers)
    menu_keywords = json.loads(menu_keywords.text)
    while True:
        state = GPIO.input(BUTTON)

        if not state and not button:
            recording_thread.start()
            lights.change(255, 255, 255)
            button = True

        if state and button:
            lights.change(255, 0, 0)
            wave_output = recording_thread.stop()
            recording_thread.join()
            # reinitialize thread
            recording_thread = Record(pyaudio.PyAudio())

            speech_processing = SpeechProcessing(wave_output)

            google = SpeechProcessingThreads.GoogleSpeech(speech_processing, menu_keywords)
            google.start()

            wit = SpeechProcessingThreads.WitAi(speech_processing)
            wit.start()

            bing = SpeechProcessingThreads.BingVoice(speech_processing)
            bing.start()

            google.join()
            wit.join()
            bing.join()

            lights.change(0, 0, 0)
            button = False


if __name__ == "__main__":
    main()
