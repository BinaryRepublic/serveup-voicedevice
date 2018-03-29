import requests
import json
import os

import helper.encode_multipart as formdata

from helper.toml_loader import Config
cfg = Config("config.toml")


class OrderRequest:
    def __init__(self, ro_auth, voice_device):
        self.cfg = cfg.load()
        self.orderApi = {
            "url": self.cfg["orderApi"]["host"] + ":" + str(self.cfg["orderApi"]["port"]) + "/order",
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
        }
        self.analyzeApi = {
            "url": self.cfg["analyzeApi"]["host"] + ":" + str(self.cfg["analyzeApi"]["port"]) + "/order",
            "headers": {
                'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                'Content-Type': "application/json",
                'Cache-Control': "no-cache",
                'Postman-Token': "7437f00e-f217-5351-e086-cb8729799eda"
            }
        }
        self.ro_auth = ro_auth
        self.voice_device = voice_device

    def request(self, order):
        # add authentication headers
        self.orderApi["headers"]["Access-Token"] = self.ro_auth.access()
        # ORDER-API
        order_api = requests.post(self.orderApi["url"],
                                  data=json.dumps({'order': order, 'voiceDeviceId': self.voice_device["id"]}),
                                  headers=self.orderApi["headers"])
        order_api_text = json.loads(order_api.text)

        if order_api.status_code != 200:
            return None
        elif self.analyzeApi["url"] and "id" in order_api_text:
            file_dir = "soundfiles/"
            file_src = file_dir + "new.wav"

            file_dest_name = order_api_text["id"] + ".wav"
            file_dest = file_dir + file_dest_name

            os.rename(file_src, file_dest)
            file = open(file_dest, "r")

            fields = {'order-id': order_api_text["id"]}
            print(fields)
            print(self.analyzeApi["url"])
            files = {'soundfile': {'filename': file_dest_name, 'content': file.read()}}
            data, headers = formdata.encode_multipart(fields, files)
            headers["Access-Token"] = self.ro_auth.access()
            analyze_api = requests.post(self.analyzeApi["url"],
                                        data=data,
                                        headers=headers)
            print(analyze_api)
            print(analyze_api.text)
            analyze_api_text = json.loads(analyze_api.text)
            print("order_id:       " + analyze_api_text["id"])
            print("soundfile-path: " + analyze_api_text["soundfile-path"])

        return order_api_text
