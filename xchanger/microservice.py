import requests
import logging
import os

def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}

class MicroService:
    def __init__(self, name, url):
        self.SERVICE_NAME = name
        self.SERVICE_URL = url
        self.TEST_USERNAME = os.environ.get("TEST_USERNAME")
        self.TEST_PASSWORD = os.environ.get("TEST_PASSWORD")

    def get_token(self, security_route_name, security_route_key):
        try:
            r = requests.post(self.SERVICE_URL + security_route_name,
                              json=dict(username=self.TEST_USERNAME, password=self.TEST_PASSWORD))
            print(r)
            r.raise_for_status()

        except requests.exceptions.HTTPError as err:
            logging.error(err)
            return None
        return r.json()[security_route_key]

    def contact_service(self, security_route_name, security_route_key, message_route_name, message_body_dict):

        access_token = self.get_token(security_route_name, security_route_key)
        if access_token:
            try:
                response = requests.post(self.SERVICE_URL + message_route_name, json=message_body_dict,
                                         headers=make_headers(access_token))
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                logging.error(err)
                return None

            return response.json()
        else:
            logging.error("No access token retrieved")
            return None
