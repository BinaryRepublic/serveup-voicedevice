from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google_speech_streaming import GoogleMicrophoneStream

from lights import Lights

import requests
import threading
Thread = threading.Thread

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class OrderingRecording(Thread):
    def __init__(self, audio_interface):
        self.stopped = False
        Thread.__init__(self)
        self.audio_interface = audio_interface
        self.client = speech.SpeechClient()
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code='de')
        self.streaming_config = types.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True)
        self.stream = None
        self.responses = None
        self.order = ''

        self.lights = Lights(3)

    def run(self):
        with GoogleMicrophoneStream(self.audio_interface, RATE, CHUNK) as stream:
            self.stream = stream
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            self.responses = self.client.streaming_recognize(self.streaming_config, requests)

            # Now, put the transcription responses to use.
            self.listen_print_loop()

    def listen_print_loop(self):

        self.lights.change(255, 255, 255)

        num_chars_printed = 0

        for response in self.responses:
            print(response)
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                num_chars_printed = len(transcript)

            else:
                num_chars_printed = 0
                if self.stopped:
                    self.order = transcript + overwrite_chars
                    self.order = self.order.encode("utf-8")
                    break

        # final order request to order-api
        self.order_request()

    def order_request(self):
        print(self.order)
        url = "http://138.68.71.39:3000/apporder"
        payload = "{\n\t\"order\":\"" + self.order + "\"\n}"
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

    def stop(self):
        self.stopped = True
