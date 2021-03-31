from unittest import TestCase
from unittest.mock import patch
from xchanger.microservice import MicroService
from munch import Munch

class MockResponse:
    def __init__(self, json_data, status_code, reason):
        self.json_data = json_data
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return self.json_data

def mocked_requests_post(*args, **kwargs):
    if args[0] == 'http://test.service.ac.uk/api/login':
        return MockResponse({"token": "faketoken"}, 201,"")
    elif args[0] == 'http://test.service.ac.uk/api/receive_messages':
        return MockResponse({"job": "Job succeed"}, 200,"")

    return MockResponse(None, 404, "URL NOT FOUND")

class TestMicroservice(TestCase):
    def setUp(self):
        self.config = Munch({"service_name": "test_service",
                    "service_url": "http://test.service.ac.uk/api/",
                    "security_route_name": "login",
                    "security_route_key" : "token",
                    "message_route_name": "receive_messages",
                    "message_route_key":"message",
                    "username": "myuser",
                    "password":"mypassword"})

    @patch('xchanger.microservice.requests.head')
    def test_microservice_setup_from_config(self, mock_head):

        mock_head.return_value = MockResponse({'headers':'fake_headers'}, 200, "")

        service = MicroService(self.config.service_name, self.config.service_url, self.config.username,
                               self.config.password)
        service.test_service_connection(security_route_name=self.config.security_route_name)
        self.assertTrue(mock_head.called)
        self.assertEqual(mock_head.call_args[0][0], "http://test.service.ac.uk/api/login")

    @patch('xchanger.microservice.requests.post', side_effect=mocked_requests_post)
    def test_contact_service(self, mock_post):
        service = MicroService(self.config.service_name, self.config.service_url, self.config.username,
                               self.config.password)
        message_body_dict = dict(message="my message")
        r = service.contact_service(self.config.security_route_name,
                                self.config.security_route_key,
                                self.config.message_route_name, message_body_dict)
        self.assertEqual(mock_post.call_args[0][0], "http://test.service.ac.uk/api/receive_messages")
        self.assertEqual(r.json(),{'job': 'Job succeed'})


class TestPikaConnection(TestCase):
    def setUp(self) -> None:
        pass

    def connect_to_pika(self):
        #good connection
        #bad connection
        pass

