# microphone
from record import Record
import pyaudio
# button
import RPi.GPIO as GPIO
# lights
from lights import Lights
# libraries
from speech_processing import SpeechProcessing
from ordering import Ordering

from threading import Thread

ordering = Ordering("http://138.68.71.39:3000/apporder")


def request_output(order):
    print('ORDER: ' + order)
    result = ordering.request(order)
    for item in result:
        print('----')
        print(item['name'])
        print(item['nb'])
        print(item['size'])


class GoogleSpeech(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.google_speech()
        print('\n\n---------------- GOOGLE SPEECH ----------------')
        request_output(order)


class WitAi(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.wit_ai()
        print('\n\n---------------- WIT AI ----------------')
        request_output(order)


class BingVoice(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.bing()
        print('\n\n---------------- BING VOICE ----------------')
        request_output(order)


def main():
    BUTTON = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    button = False

    lights = Lights(3)

    recording_thread = Record(pyaudio.PyAudio())

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

            # wave_output = 'record9.wav' TEST
            speech_processing = SpeechProcessing(wave_output)

            google = GoogleSpeech(speech_processing)
            google.start()

            wit = WitAi(speech_processing)
            wit.start()

            bing = BingVoice(speech_processing)
            bing.start()

            google.join()
            wit.join()
            bing.join()

            lights.change(0, 0, 0)
            button = False


if __name__ == "__main__":
    main()
