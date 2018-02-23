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

ordering = Ordering("http://138.68.71.39:3000/order")
ordering_getonly = Ordering("http://138.68.71.39:3000/order?getonly=1")


def request_output(order, headline, getonly=False):
    print('ORDER: ' + order)
    if not getonly:
        result = ordering.request(order)
    else:
        result = ordering_getonly.request(order)

    print(headline)
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
        request_output(order, '\n\n---------------- GOOGLE SPEECH ----------------')


class WitAi(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.wit_ai()
        request_output(order, '\n\n---------------- WIT AI ----------------', True)


class BingVoice(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.bing()
        request_output(order, '\n\n---------------- BING VOICE ----------------', True)


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
