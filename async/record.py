import os
import pyaudio
import threading
import wave
Thread = threading.Thread

FORMAT = pyaudio.paInt16
# CHANNELS = 2
CHANNELS = 1
# RATE = 44100
RATE = 16000
CHUNK = 1024


class Record(Thread):
    def __init__(self, audio_interface):
        Thread.__init__(self)

        self.audio_interface = audio_interface

        filename_prefix = "record"
        filename_nb = 0
        file_type = ".wav"
        while os.path.isfile(filename_prefix + str(filename_nb) + file_type):
            filename_nb += 1
        self.filename = filename_prefix + str(filename_nb) + file_type

        self.stream = None
        self.frames = []
        self.stopped = False

    def run(self):
        print('thread started')
        self.stream = self.audio_interface.open(format=FORMAT, channels=CHANNELS,
                                 rate=RATE, input=True,
                                 frames_per_buffer=CHUNK)
        print("recording...")
        self.frames = []
        while not self.stopped:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()

        wave_file = wave.open(self.filename, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio_interface.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
        print("finished recording")

    def stop(self):
        self.stopped = True
        return self.filename
