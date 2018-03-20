# libraries
import os
import requests
import time
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
from ordering.order_request import OrderRequest

# authentication
from authentication.auth import Authentication

ro_auth = Authentication()
ro_auth.login()

# initialize orderRequest
orderRequest = OrderRequest(ro_auth)


def check_connection(host):
    # check connection
    response = os.system("ping -c 1 " + host)
    while response != 0:
        response = os.system("ping -c 1 " + host)
        lights_change(255, 0, 0, 5, 1)
        time.sleep(10)


def lights_change(r, g, b, intensity=100, duration=0):
    lights = Lights("change", {
        "r": r,
        "g": g,
        "b": b,
        "intensity": intensity,
        "duration": duration
    })
    lights.start()
    lights.join()


def result_output(order, result, headline):
    print(headline)
    if result:
        print('ORDER: ' + order)

        for item in result["items"]:
            print('----')
            print(item['name'])
            print(item['nb'])
            print(item['size'])


def main():
    # prepare button interface
    BUTTON = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    button = False

    # initialize recording thread
    recording_thread = Record(pyaudio.PyAudio())

    # make sure microServices are available
    check_connection("138.68.71.39")

    # start main loop
    while True:
        state = GPIO.input(BUTTON)

        if not state and not button:
            check_connection("138.68.71.39")
            recording_thread.start()
            lights_change(255, 255, 255)
            button = True

        if state and button:
            lights = Lights("pulse", {"r": 255, "g": 255, "b": 255})
            lights.start()

            recording_thread.stop()
            wave_output = recording_thread.join()

            if wave_output:
                # reinitialize thread
                recording_thread = Record(pyaudio.PyAudio())
                speech_processing = SpeechProcessing(wave_output, ro_auth)

                google = SpeechProcessingThreads.GoogleSpeech(speech_processing)
                google.start()

                wit = SpeechProcessingThreads.WitAi(speech_processing)
                wit.start()

                bing = SpeechProcessingThreads.BingVoice(speech_processing)
                bing.start()

                result = {
                    "items": []
                }

                order = bing.join()
                if order:
                    result = orderRequest.request(order)
                print_headline = 'BING'

                if not len(result["items"]):
                    order = wit.join()
                    if order:
                        result = orderRequest.request(order)
                    print_headline = 'WIT AI'

                    if not len(result["items"]):
                        print_headline = 'GOOGLE'
                        if order:
                            result = orderRequest.request(order)
                        order = google.join()
                if order:
                    print(print_headline + ' order: ' + order)
            else:
                order = False
                print_headline = False

            lights.stop()
            lights.join()

            if wave_output:
                if len(result["items"]):
                    lights_change(r=0, g=255, b=0, duration=1)
                    result_output(order, result, '------------- ' + print_headline + ' -------------')
                else:
                    lights_change(r=255, g=0, b=0, duration=1)
            else:
                lights_change(0, 0, 0)
                # reinitialize thread
                recording_thread = Record(pyaudio.PyAudio())

            button = False


if __name__ == "__main__":
    main()
