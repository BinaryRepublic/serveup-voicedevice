import requests
import json
from helper.toml_loader import Config

import datetime

config = Config("config.toml")


class Authentication:
    def __init__(self):
        auth_config = config.load()
        # credentials
        self.credentials = auth_config["roCredentials"]
        # get grant
        self.cred_host = auth_config["orderApi"]["host"]
        self.cred_port = auth_config["orderApi"]["port"]
        self.cred_headers = {
            "Content-Type": "application/json"
        }
        # token handling
        self.auth_host = auth_config["authApi"]["host"]
        self.auth_port = auth_config["authApi"]["port"]
        self.auth_headers = self.cred_headers
        # tokens
        self.access_token = None
        self.expire = None
        self.refresh_token = None

    @staticmethod
    def datetime(date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")

    def login(self):
        # ----------------- AUTH DISABLED
        # return ""
        # get grant
        response = requests.post(self.cred_host + ":" + str(self.cred_port) + "/login",
                                 data=json.dumps({
                                     "mail": self.credentials["mail"],
                                     "password": self.credentials["password"]
                                 }), headers=self.cred_headers)
        if response.status_code == 200:
            response = response.json()
            grant = response["grant"]
            # get access and refresh token
            response = requests.post(self.auth_host + ":" + str(self.auth_port) + "/access/grant",
                                     data=json.dumps({
                                        "grant": grant
                                     }), headers=self.auth_headers)
            print(response)
            print(response.text)
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["accessToken"]
                self.expire = self.datetime(tokens["expire"])
                self.refresh_token = tokens["refreshToken"]
                return self.access_token

        return False

    def access(self):
        # ----------------- AUTH DISABLED
        # return ""
        if datetime.datetime.now() < self.expire:
            return self.access_token
        else:
            return self.refresh()

    def refresh(self):
        response = requests.post(self.auth_host + ":" + str(self.auth_port) + "/access/refresh",
                                 data=json.dumps({
                                     "refreshToken": self.refresh_token
                                 }), headers=self.auth_headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["accessToken"]
            self.expire = self.datetime(tokens["expire"])
            self.refresh_token = tokens["refreshToken"]
            return self.access_token

    def logout(self):
        # logout request to authAPI
        print("logout")
