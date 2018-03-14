from threading import Thread


class GoogleSpeech(Thread):
    def __init__(self, speech_processing, menu_keywords):
        Thread.__init__(self)
        self.speech_processing = speech_processing
        self.menu_keywords = menu_keywords
        self._return = False

    def run(self):
        order = self.speech_processing.google_speech(self.menu_keywords)
        self._return = order

    def join(self):
        Thread.join(self)
        return self._return


class WitAi(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing
        self._return = False

    def run(self):
        order = self.speech_processing.wit_ai()
        self._return = order

    def join(self):
        Thread.join(self)
        return self._return


class BingVoice(Thread):
    def __init__(self, speech_processing):
        Thread.__init__(self)
        self.speech_processing = speech_processing
        self._return = False

    def run(self):
        order = self.speech_processing.bing()
        self._return = order

    def join(self):
        Thread.join(self)
        return self._return