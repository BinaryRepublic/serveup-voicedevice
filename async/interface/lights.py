from interface import apa102
import threading
from threading import Thread
import math
import time


class Lights(Thread):
    def __init__(self, effect, effect_params):
        Thread.__init__(self)
        self.number = 3
        self.led = apa102.APA102(num_led=3)
        self.effect = effect
        self.effect_params = effect_params
        self._stop_event = threading.Event()

    def run(self):
        if self.effect == "change":
            self.change(self.effect_params["r"], self.effect_params["g"], self.effect_params["b"], self.effect_params["intensity"], self.effect_params["duration"])
        elif self.effect == "pulse":
            self.pulse(self.effect_params["r"], self.effect_params["g"], self.effect_params["b"])

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def change(self, r, g, b, intensity=100, duration=0):
        for x in range(0, self.number):
            self.led.set_pixel(x, r, g, b, intensity)
        self.led.show()
        if duration != 0:
            time.sleep(duration)
            self.change(0, 0, 0, 0)

    def pulse(self, r, g, b):
        # add speed and intensity range later
        t = 0

        while not self.stopped():
            intensity = math.sin(t - (3 * math.pi / 2)) / 2 + 0.5
            self.change(r, g, b, int(round(intensity*100)))
            t = t+0.4
            time.sleep(0.1)
