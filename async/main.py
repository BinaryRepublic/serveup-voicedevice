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
from ordering.order_request import OrderRequest

orderRequest = OrderRequest("http://138.68.71.39:3200/order", "http://138.68.71.39:5200/order")
# orderRequest_getOnly = OrderRequest("http://138.68.71.39:3200/order?getonly=1", False)


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
    BUTTON = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    button = False

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
            lights_change(255, 255, 255)
            button = True

        if state and button:
            lights = Lights("pulse", {"r": 255, "g": 255, "b": 255})
            lights.start()

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

            order = bing.join()
            print_headline = 'BING'
            if not order:
                order = wit.join()
                print_headline = 'WIT AI'
                if not order:
                    print_headline = 'GOOGLE'
                    order = google.join()

            result = orderRequest.request(order)

            lights.stop()
            lights.join()

            if result:
                lights_change(r=0, g=255, b=0, duration=1)
                result_output(order, result, '------------- ' + print_headline + ' -------------')
            else:
                lights_change(r=255, g=0, b=0, duration=1)

            button = False


if __name__ == "__main__":
    main()
