import unittest

class TestMicroservice(unittest.TestCase):
    def setUp(self):
        config = {"service_name": "test_service",
                    "service_url": "http://test.service.ac.uk",
                    "security_route_name": "login",
                    "message_route_name": "receive_messages",
                    "message_route_key":"token"}

    def test_microservice_setup_from_config(self):
        pass