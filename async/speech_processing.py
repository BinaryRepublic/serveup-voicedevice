# from speech_processing_google import SpeechProcessingGoogle
import speech_recognition as sr
from os import path
import json


class SpeechProcessing:
    def __init__(self, filename):
        self.filename = filename
        audio_file = path.join(path.dirname(path.realpath(__file__)), self.filename)
        # use the audio file as the audio source
        self.r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            self.audio = self.r.record(source)  # read the entire audio file

    def google_speech(self, menu_keywords):
        print(menu_keywords)
        google_speech_key = json.dumps(json.load(open('google_speech_credentials.json')))
        try:
            return self.r.recognize_google_cloud(self.audio,
                                                 credentials_json=google_speech_key,
                                                 language='de',
                                                 preferred_phrases=menu_keywords)
        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Cloud Speech service; {0}".format(e))

    def wit_ai(self):
        wit_ai_key = "QUP6M2CPSIMAEYK7JHLM4MWRPHEZRE2C"
        try:
            return self.r.recognize_wit(self.audio, key=wit_ai_key)
        except sr.UnknownValueError:
            print("Wit.ai could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))

    def bing(self):
        bing_key = "5284adad41b44f98bf439c2bb4e62f8a"
        try:
            return self.r.recognize_bing(self.audio, key=bing_key, language='de-DE')
        except sr.UnknownValueError:
            print("Microsoft Bing Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))


'''
------------ ENGLISH ONLY API'S

# recognize speech using Houndify
HOUNDIFY_CLIENT_ID = "INSERT HOUNDIFY CLIENT ID HERE"  # Houndify client IDs are Base64-encoded strings
HOUNDIFY_CLIENT_KEY = "INSERT HOUNDIFY CLIENT KEY HERE"  # Houndify client keys are Base64-encoded strings
try:
    print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
except sr.UnknownValueError:
    print("Houndify could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Houndify service; {0}".format(e))

# recognize speech using IBM Speech to Text
IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE"  # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE"  # IBM Speech to Text passwords are mixed-case alphanumeric strings
try:
    print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
except sr.UnknownValueError:
    print("IBM Speech to Text could not understand audio")
except sr.RequestError as e:
    print("Could not request results from IBM Speech to Text service; {0}".format(e))
'''
