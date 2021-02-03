import pika
import os
import yaml
import sys
import logging
import dotenv
from microservice import MicroService
from munch import Munch

dotenv.load_dotenv()


TEST_USERNAME = os.environ.get('TEST_USERNAME')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
LOG_PATH = os.environ.get('LOG_PATH')
CONFIG_PATH = os.environ.get('CONFIG_PATH')

logging.basicConfig(filename=LOG_PATH + 'example.log', level=logging.INFO)

def read_microservice_config(config_path):
    try:
        microservice_config = yaml.load(config_path)
    except Exception as e:
        logging.error(e)
        return None
    microservice_config = Munch(microservice_config)
    return microservice_config


def main():
    # connect to rabbitmq
    parameters = pika.connection.URLParameters(os.environ.get('AMPQ_URI'))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # set up microservice
    service_config = read_microservice_config(CONFIG_PATH)
    service = MicroService(service_config.service_name, service_config.service_url)


    def callback(ch, method, properties, body):
        logging.info(" [x] Received from rabbitmq")
        logging.info("retrieving message...")

        if body is not None:
            response = service.contact_service(service_config.security_route_name,
                                               service_config.message_route_name,
                                               {service_config.message_route_key: body.decode()})
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
