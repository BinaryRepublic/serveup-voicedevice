# microphone
import pyaudio

# button
import RPi.GPIO as GPIO

# lights
from lights import Lights

# environment
import os
import requests
from ordering import OrderingRecording

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_speech_credentials.json'

url = "http://138.68.71.39:3000/orderkeywords"
headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache"
}
menu_keywords = requests.request("GET", url, headers=headers)


def main():
    lights = Lights(3)

    button = False
    voice_rec_thread = OrderingRecording(pyaudio.PyAudio(), menu_keywords)
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
            voice_rec_thread = OrderingRecording(pyaudio.PyAudio(), menu_keywords)
            lights.change(0, 0, 0)
            button = False


if __name__ == '__main__':
    main()
