import pika
import os
import requests
import ast
import sys
import logging
import dotenv

dotenv.load_dotenv()


TEST_USERNAME = os.environ.get('TEST_USERNAME')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
SERVICE_URL = os.environ.get('STORE_URL')
LOG_PATH = os.environ.get('LOG_PATH')

logging.basicConfig(filename=LOG_PATH + 'example.log', level=logging.INFO)


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


def contact_service(body):
    try:
        r = requests.post(SERVICE_URL + "token", json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        access_token = r.json()['access_token']
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None

    try:
        response = requests.post(SERVICE_URL + 'receive_async_messages', json=body,
                                 headers=make_headers(access_token))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None

    return response.json()


def main():

    parameters = pika.connection.URLParameters(os.environ.get('AMPQ_URI'))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        logging.info(" [x] Received from rabbitmq")
        logging.info("retrieving message...")
        print(body)
        if body is not None:
                 response = contact_service(body)
                 logging.info(response.status())

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info('presigned URL returned')

    channel.basic_consume(queue='client.jobs.write', on_message_callback=callback)

    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
