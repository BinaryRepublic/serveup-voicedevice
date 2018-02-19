#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START import_libraries]
from __future__ import division

import apa102

import re
import sys
import os
import time
import requests
import threading

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

import RPi.GPIO as GPIO

Thread = threading.Thread

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

# [END import_libraries]

# cred_file = open('../../../google_speech_credentials.json')
# GOOGLE_CLOUD_SPEECH_CREDENTIALS = cred_file.read()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_speech_credentials.json'

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, audio_interface, rate, chunk):
        self._audio_interface = audio_interface
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]


class VoiceRec(Thread):
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

    def run(self):
        with MicrophoneStream(self.audio_interface, RATE, CHUNK) as stream:
            self.stream = stream
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            self.responses = self.client.streaming_recognize(self.streaming_config, requests)

            # Now, put the transcription responses to use.
            self.listen_print_loop()

    def listen_print_loop(self):

        listening_lights(255, 255, 255)

        """Iterates through server responses and prints them.
        
        The responses passed is a generator that will block until a response
        is provided by the server.
        
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
        
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        time_count_start = 0
        time_over = 0
        for response in self.responses:

            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                # sys.stdout.write(transcript + overwrite_chars + '\r')
                # sys.stdout.flush()
                num_chars_printed = len(transcript)

            else:
                # print(transcript + overwrite_chars)
                num_chars_printed = 0
                if self.stopped:
                    self.order = transcript + overwrite_chars
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


led = apa102.APA102(num_led=3)


def listening_lights(r, g, b):
    led.set_pixel(0, r, g, b, 100)
    led.set_pixel(1, r, g, b, 100)
    led.set_pixel(2, r, g, b, 100)
    led.show()


def main():

    button = False
    voice_rec_thread = VoiceRec(pyaudio.PyAudio())
    print('ready')
    while True:
        state = GPIO.input(BUTTON)

        if not state and not button:
            voice_rec_thread.start()
            button = True

        if state and button:
            listening_lights(255, 0, 0)
            voice_rec_thread.stop()
            voice_rec_thread.join(5)
            voice_rec_thread = VoiceRec(pyaudio.PyAudio())
            listening_lights(0, 0, 0)
            button = False


if __name__ == '__main__':
    main()
