import pyaudio
import threading
import wave

from interface.lights import Lights

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
        self.filedir = "soundfiles/"
        self.filename = "new.wav"

        self.stream = None
        self.frames = []
        self.tooShort = False
        self.stopped = False

    def run(self):
        print('thread started')
        self.stream = self.audio_interface.open(format=FORMAT, channels=CHANNELS,
                                                rate=RATE, input=True,
                                                frames_per_buffer=CHUNK)
        lights = Lights("change", {"r": 255, "g": 255, "b": 255, "intensity": 100, "duration": 0})
        lights.start()
        lights.join()

        print("recording...")
        self.frames = []
        while not self.stopped:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()

        wave_file = wave.open(self.filedir + self.filename, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio_interface.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(self.frames))

        # check duration
        frames = wave_file.getnframes()
        rate = wave_file.getframerate()
        duration = frames / float(rate)

        wave_file.close()
        print("finished recording")

        if duration < 1:
            self.tooShort = True
            print("wave too short")

    def stop(self):
        self.stopped = True

    def join(self):
        Thread.join(self)
        if not self.tooShort:
            return self.filename
        else:
            return False
