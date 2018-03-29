# libraries
import os
import requests
import time
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

# config
from helper.toml_loader import Config

# authentication
from authentication.auth import Authentication


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

        if len(result["drinks"]):
            print('---- DRINKS')
            for drink in result["drinks"]:
                print(drink['name'])
                print(drink['nb'])
                print(drink['size'])
                print('---')

        if len(result["services"]):
            print('---- SERVICES')
            for service in result["services"]:
                print(service['name'])
                print('---')


def main():
    # authentication
    ro_auth = Authentication()
    ro_auth.login()

    # load config
    config = Config("config.toml")
    cfg = config.load()

    # prepare button interface
    BUTTON = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    button = False

    # initialize recording thread
    recording_thread = Record(pyaudio.PyAudio())

    # make sure microServices are available
    check_connection("138.68.71.39")

    # get voiceDevice info
    url = cfg["adminApi"]["host"] + ":" + str(cfg["adminApi"]["port"])
    url += "/voicedevice/" + cfg["roCredentials"]["voiceDeviceId"]
    print(url)
    headers = {
        "Access-Token": ro_auth.access()
    }
    print(headers)
    response = requests.get(url, headers=headers)
    voice_device = None
    print(response)
    print(response.text)
    if response.status_code == 200:
        voice_device = response.json()

    # initialize orderRequest
    order_request = OrderRequest(ro_auth, voice_device)

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
                speech_processing = SpeechProcessing(wave_output, ro_auth, voice_device)

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
                    result = order_request.request(order)
                print_headline = 'BING'

                if not order or (not len(result["drinks"]) and not len(result["services"])):
                    order = wit.join()
                    if order:
                        result = order_request.request(order)
                    print_headline = 'WIT AI'

                    if not order or (not len(result["drinks"]) and not len(result["services"])):
                        print_headline = 'GOOGLE'
                        if order:
                            result = order_request.request(order)
                        order = google.join()
                if order:
                    print(print_headline + ' order: ' + order)
            else:
                order = False
                print_headline = False

            lights.stop()
            lights.join()

            if wave_output:
                if order and (len(result["drinks"]) or len(result["services"])):
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
