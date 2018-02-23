import requests
import json


class Ordering:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
        }

    def request(self, order):
        response = requests.post(self.url, data=json.dumps({'order': order}), headers=self.headers)
        if response.status_code != 200:
            print(order)
            print(response.text)
            return None
        else:
            return json.loads(response.text)
