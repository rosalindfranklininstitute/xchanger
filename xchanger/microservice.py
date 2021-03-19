import requests
import logging
import os

logger = logging.getLogger(__name__)


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


class MicroService:
    def __init__(self, name, url):
        self.SERVICE_NAME = name
        self.SERVICE_URL = url
        self.TEST_USERNAME = os.environ.get("TEST_USERNAME")
        self.TEST_PASSWORD = os.environ.get("TEST_PASSWORD")

    def get_token(self, security_route_name, security_route_key):

        r = requests.post(self.SERVICE_URL + security_route_name,
                              json=dict(username=self.TEST_USERNAME, password=self.TEST_PASSWORD))
        logger.info(f'login into {self.SERVICE_NAME}: {r.status_code}')

        if r.status_code == 201:
            logger.info("Access Token Granted")
            token = r.json()[security_route_key]
            return token
        else:
            return None


    def contact_service(self, security_route_name, security_route_key, message_route_name, message_body_dict):

        access_token = self.get_token(security_route_name, security_route_key)
        logger.info(self.SERVICE_URL + message_route_name)
        if access_token:
            logger.info("posting message to service")
            response = requests.post(self.SERVICE_URL + message_route_name, json=message_body_dict,
                                         headers=make_headers(access_token))
            if response.status_code ==200:
                return response
            else:
                logger.debug(f'Posting to {self.SERVICE_URL}{message_route_name} result: {response.status_code}{response.reason} ')
                return None


    def test_service_connection(self, **kwargs):
         """Start up method to check we can access the url"""
         # ping url to check it is there
         try:
             r = requests.head(self.SERVICE_URL)
             logger.info(f'service base url ping: {r.status_code}, {r.reason}')
         except ConnectionError as e:
             logger.error(e)
         try:
             for k in kwargs.values():
                r =requests.head(self.SERVICE_URL + k)
                logger.info(f'service routes {k} ping: {r.status_code}, {r.reason}')
         except ConnectionError as e:
              logger.error(e)

