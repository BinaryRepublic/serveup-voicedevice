from threading import Thread
from ordering.order_request import Ordering

ordering = Ordering("http://138.68.71.39:3200/order", "http://138.68.71.39:5200/order")
ordering_getonly = Ordering("http://138.68.71.39:3200/order?getonly=1", False)


def request_output(order, headline, getonly=False):
    print(headline)
    if order:
        print('ORDER: ' + order)
        if not getonly:
            result = ordering.request(order)
        else:
            result = ordering_getonly.request(order)

        for item in result["items"]:
            print('----')
            print(item['name'])
            print(item['nb'])
            print(item['size'])


class GoogleSpeech(Thread):
    def __init__(self, speech_processing, menu_keywords):
        Thread.__init__(self)
        self.speech_processing = speech_processing
        self.menu_keywords = menu_keywords

    def run(self):
        order = self.speech_processing.google_speech(self.menu_keywords)
        request_output(order, '\n\n---------------- GOOGLE SPEECH ----------------')


class WitAi(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.wit_ai()
        request_output(order, '\n\n---------------- WIT AI ----------------', True)


class BingVoice(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing

    def run(self):
        order = self.speech_processing.bing()
        request_output(order, '\n\n---------------- BING VOICE ----------------', True)