import apa102


class Lights:
    def __init__(self, number):
        self.number = number
        self.led = apa102.APA102(num_led=number)

    def change(self, r, g, b):
        for x in range(0, self.number):
            self.led.set_pixel(x, r, g, b, 100)
        self.led.show()
