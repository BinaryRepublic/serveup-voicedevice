# microphone
import pyaudio

# button
import RPi.GPIO as GPIO

# lights
from lights import Lights

# environment
import os
from ordering import OrderingRecording

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_speech_credentials.json'


def main():
    lights = Lights(3)

    button = False
    voice_rec_thread = OrderingRecording(pyaudio.PyAudio())
    print('ready')
    while True:
        state = GPIO.input(BUTTON)

        if not state and not button:
            voice_rec_thread.start()
            button = True

        if state and button:
            lights.change(255, 0, 0)
            voice_rec_thread.stop()
            voice_rec_thread.join(5)
            voice_rec_thread = OrderingRecording(pyaudio.PyAudio())
            lights.change(0, 0, 0)
            button = False


if __name__ == '__main__':
    main()
