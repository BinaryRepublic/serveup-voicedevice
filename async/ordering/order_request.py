import requests
import json
import os

import helper.encode_multipart as formdata


class Ordering:
    def __init__(self, order_api_url, analyze_api_url):
        self.orderApi = {
            "url": order_api_url,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
        }
        self.analyzeApi = {
            "url": analyze_api_url,
            "headers": {
                'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                'Content-Type': "application/json",
                'Cache-Control': "no-cache",
                'Postman-Token': "7437f00e-f217-5351-e086-cb8729799eda"
            }
        }

    def request(self, order):
        # ORDER-API
        order_api = requests.post(self.orderApi["url"],
                                  data=json.dumps({'order': order}),
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
            files = {'soundfile': {'filename': file_dest_name, 'content': file.read()}}
            data, headers = formdata.encode_multipart(fields, files)
            analyze_api = requests.post(self.analyzeApi["url"],
                                        data=data,
                                        headers=headers)
            analyze_api_text = json.loads(analyze_api.text)
            print("order_id:       " + analyze_api_text["id"])
            print("soundfile-path: " + analyze_api_text["soundfile-path"])

        return order_api_text
